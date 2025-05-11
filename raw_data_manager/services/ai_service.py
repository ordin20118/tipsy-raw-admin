from raw_data_manager.models import CrawledLiquor, CrawledLiquorTag, RawLiquor, SearchLiquorArticleQueue
import logging
from django.db import transaction
from core.openai_settings import OPENAI_SECRET_KEY, OPENAI_URL_PROMPT
from raw_data_manager.repositories.search_liquor_article_queue_repository import SearchLiquorArticleQueueRepository
from raw_data_manager.services.article_service import ArticleService
from datetime import datetime
from duckduckgo_search import DDGS
from raw_data_manager.services.liquor_service import LiquorService
import trafilatura
import openai
import requests
import json
import re

logger = logging.getLogger('django')
class AiService:
    def __init__(self):
        self.article_service = ArticleService()
        self.liquor_service = LiquorService()
  
    def extract_json(self, response: str) -> dict:
        """LLM 응답에서 불필요한 코드 블록 및 텍스트 제거 후 JSON 파싱"""
        cleaned_text = response
        if '```json' in response:
            cleaned_text = re.sub(r"^```json\n|\n```$", "", response.strip())  # ```json\n 및 \n``` 제거
        cleaned_text = cleaned_text.replace("\n", "")
        return json.loads(cleaned_text)  # JSON 파싱

    # 순수 덕덕고 검색
    def search_duckduckgo(self, keyword, max_results=1):
        results = DDGS().text(keywords=keyword, safesearch='off', max_results=max_results)
        # for i, result in enumerate(results):
            #print(f"{i+1}: {result['title']} - {result['href']}")
            # print(f"{i+1}: {result}\n")
            # print({result['body']})
        return results

    def chat_with_gpt(self, prompt):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            #model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
            #max_tokens=150  # 응답의 최대 토큰 수 (필요에 따라 조정)
        )
        return response.choices[0].message.content

    #@transaction.atomic
    def search_liquor_article_and_save(self, queue: SearchLiquorArticleQueue):
        # 키워드로 duckduckgo 검색
        docs = self.search_duckduckgo(queue.keyword, queue.target_search_count)

        queue.searched_count = len(docs)
        collected_count = 0
        dup_count = 0
        failed_count = 0        
        for doc in docs:
            logger.info("[ ## Start Collect Article ##]")
            logger.info(f"[URL]:{doc['href']}")
            doc_title = doc['title']
            logger.info(f"[title]:{doc['title']}")
            try:
                # 문서 파싱
                # html 다운로드
                origin_html = trafilatura.fetch_url(doc['href'])
                
                # 다운로드 된 HTML에서 내용 추출
                extracted_text = trafilatura.extract(origin_html)

                # 추출된 콘텐츠 확인
                if extracted_text:
                    pass
                    #logger.info(f"[EXTRACTED]:{extracted_text}")
                else:
                    logger.info("HTML 문서에서 콘텐츠를 추출할 수 없습니다.")
                    failed_count += 1
                    continue

                # 추출된 내용에서 AI에게 중요한 내용과 함께 요약 요청
                prompt = self.get_extract_document_prompt(extracted_text)
                ai_response = self.chat_with_gpt(prompt)
                response_json = self.extract_json(ai_response)
                logger.info(f"[AI RESPONSE]: {ai_response}")

                # TODO: URL 중복 확인
                logger.info("[URL 중복 확인 시작]")
                prev_article = self.article_service.get_article_by_url(doc['href'])
                logger.info(f"[prev_article]:{prev_article}")

                # 아티클이 있지만 아티클과 현재 술과의 관계 데이터가 없다면 파싱 후 저장
                # 아티클과 관계 데이터 모두 있다면 파싱 과정 없이 pass 
                if prev_article != None:
                    logger.info("[URL 중복 있음]")
                    dup_count += 1
                    # 관계 데이터 조회
                    logger.info("[존재하는 아티클에 대한 관계 확인]")
                    liquor_article_rel = self.article_service.get_liquor_article_rel(queue.liquor.liquor_id, prev_article.id)
                    if liquor_article_rel != None:
                        continue
                    else:
                        # TODO: liquor-article 관계만 저장
                        logger.info(f"liquor_id:[{queue.liquor.liquor_id}]/article_id:[{prev_article.id}]/relation_score:[{response_json['relation_score']}]")
                        self.article_service.create_liquor_article_rel(queue.liquor.liquor_id, prev_article.id, response_json['relation_score'])
                        continue
                else:
                    logger.info("[URL 중복 없음]")
                    # article 데이터 저장
                    # url, title, content, state, extracted_content, score, tags
                    article_data = {
                        'url': doc['href'],
                        'title': doc_title,
                        'content': origin_html,
                        'extracted_content': response_json['content'],
                        'score': response_json['score'],
                        'tags': response_json['tags'],
                        'state': 1
                    }
                    article = self.article_service.create_article(article_data)
                    logger.info(f"[저장된 아티클] {article}")
                    
                    # save liquor-article relation
                    self.article_service.create_liquor_article_rel(queue.liquor.liquor_id, article.id, response_json['relation_score'])
                    logger.info(f"[술 아티클 관계 저장 완료]")

            except Exception as e:
                failed_count += 1
                logger.error(f"[Search Liquor Article ERROR]:{e}")
                continue
            collected_count += 1
            logger.info("[데이터 수집 완료]")

        # TODO: update queue state and stats
        queue.collected_count = collected_count
        queue.dup_count = dup_count
        queue.failed_count = failed_count
        queue.state = SearchLiquorArticleQueue.STATE_CHOICES[2][0]
        queue.save()

    def ana_articles(self, liquor_id):
        """
        [ 술에 대한 아티클들을 분석하여 본문 데이터 만들기 ]
        1. 술에 대한 아티클 5개 조회
          - 관련도가 80 이상, 아티클 자체의 점수가 80이상
        2. 본문 요약을 모아서 ai에게 본문 생성 요청
        3. 본문 데이터를 DB에 저장
          - seq, title, sub_title, content, type
        """
        logger.info(f"[ana_articles] liquor_id:{liquor_id}")
        articles = self.article_service.get_liquor_top_articles(liquor_id=liquor_id)
        
        if articles == None or len(articles) == 0:
            logger.info(f"[조회된 상위 아티클 없음]")
            return
        logger.info(f"[조회된 상위 아티클 수]:{len(articles)}")
            
        compiled_article = ""
        for article in articles:
            compiled_article += article.extracted_content

        # 여러 문서들을 바탕으로 새로운 문서 내용 만들기
        make_new_doc_prompt = self.get_make_new_doc_prompt(compiled_article)
        new_doc_response = self.chat_with_gpt(make_new_doc_prompt)
        extracted_new_doc = self.extract_json(new_doc_response)
        logger.info(f"[NEW DOC]:{extracted_new_doc}\n\n")

        self.liquor_service.save_liquor_contents(liquor_id, extracted_new_doc)

    @transaction.atomic
    def ana_description(self, crawled_liquor_id):
        # select liquor
        crawled_liquor = CrawledLiquor.objects.get(id=crawled_liquor_id)

        if crawled_liquor == None:
            return

        # request analyze to ChatGPT
        # 모델과 온도 설정
        #model = "gpt-3.5-turbo"
        model = "gpt-4o-mini"
        temperature = 0.5

        # 헤더 설정
        headers = {
            "Authorization": f"Bearer {OPENAI_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        # 시스템 프롬프트 설정
        system_prompt = """
        이제부터 당신은 술에 대한 문서를 입력으로 받는다.
        아래에서 정한 요구사항을 만족하면서, 문서에서 필요한 데이터를 추출하여
        제시하는 JSON 포맷에 맞게 출력해야 한다.

        아래는 예시의 json 포맷이다.

        JSON Format:
    
        {
        "tags": ["태그1", "태그2", "태그3"],
        "description": "본문의 '데일리샷' 관련 내용은 제외 후 내용을 400자 이내로 요약하면서 원본과는 다르게 친절하고 상큼한 느낌의 말투로 변환한다. 적절히 보기 좋게 줄바꿈 문자(\n)도 넣어준다."
        }
    
        아래는 만족해야할 요구사항이다.

        요구사항:
        1. 술의 분류, 맛과 향, 페어링 음식, 가격, 색상, 원산지, 제조법 등의 특징들에 대해서 짧은 해시태그 형태로 핵심 내용만 최대 15개까지 나열하여 tags 필드에 할당한다.
        2. 해시 태그는 가능한 짧은 단어로 표현한다.
        3. 해시태그에는 술의 이름이 있어서는 안 된다.
        4. 본문의 데일리샷 관련 내용은 제거한다.
        5. 본문 전체의 내용을 500자 이내로 요약하거나 내용이 적은 경우 화법을 친절하고 부드럽게 바꾸거나 내용의 순서를 바꾼다.
        6. 변형된 본문의 내용은 description에 필드에 할당한다.
        """

        # 유저 입력 설정
        content = crawled_liquor.description

        # 요청 데이터 설정
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "temperature": temperature
        }

        # 요청 보내기
        response = requests.post(OPENAI_URL_PROMPT, headers=headers, data=json.dumps(data))

        # 응답 처리
        if response.status_code == 200:
            res_json = response.json()
            choices = res_json.get("choices")
            if choices:
                chat_res = choices[0]
                finish_reason = chat_res.get("finish_reason")
                if finish_reason == "stop":
                    message = chat_res.get("message")
                    content_str = message.get("content")
                    content_obj = json.loads(content_str)

                    # update crawled liquor u_description
                    crawled_liquor.u_description = content_obj['description']
                    crawled_liquor.save(update_fields=['u_description'])

                    # save new tags
                    tags = content_obj['tags']

                    # check prev tag
                    for tag in tags:
                        try:
                            prev_tag = CrawledLiquorTag.objects.filter(crawled_liquor_id=crawled_liquor.id, tag=tag)
                            if prev_tag is None or len(prev_tag) == 0:
                                # save tag
                                new_tag = CrawledLiquorTag(
                                    crawled_liquor_id=crawled_liquor.id,
                                    tag=tag,
                                )
                                new_tag.save()
                        except Exception as e:
                            logger.error("", e)
                        
                    return content_obj
                elif finish_reason == "length":
                    logger.debug("[!!! 토큰이 너무 길어서 중지됨 !!!]")
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.json())

    def get_extract_document_prompt(self, doc_text):
        return f"""
        다음 문서를 분석하여 아래 정보를 JSON 형식으로 반환하세요:

        - 태그: 문서의 종류를 추출하세요. 문서가 다루고 있는 주제에 맞는 태그를 아래에서 고르세요. 여러 개의 태그를 선택할 수 있습니다.
        역사
        전통
        문화
        추천
        칵테일 레시피
        페어링
        테이스팅 가이드
        마시기 팁
        주류 상식
        주류 평가
        제조 과정
        원재료
        건강
        산업 분석
        트렌드
        시장 동향
        페스티벌
        시음회
        주류 박람회

        - 스코어: 문서의 술에 대한 정보가 얼마나 유용한지 평가하고, 0에서 100 사이의 점수를 매기세요. 0은 유용하지 않음을, 100은 매우 유용함을 의미합니다.
        술과 관련된 내용이 아니면 유용하지 않다고 판단합니다. 
        과한 광고성 내용은 유용하지 않다고 판단합니다.

        - 관련도: 문서와 키워드간의 관련도를 0에서 100 사이의 점수로 매기세요. 0은 관련 없음, 100은 매우 관련 있음을 의미합니다.
                대상 주류와 관계 없는 공통적인 문서의 경우 90 아래로 점수를 매깁니다.

        - 제목 추출: 문서의 제목을 요약하지 않고 원본 그대로 추출합니다.

        - 본문 추출: 문서 내용을 3,000자 내외로 간결하게 요약하되, 핵심적인 정보는 모두 포함하여 요약하세요. 감정적 표현이나 주관적인 판단을 배제하고, 객관적이고 사실적인 내용만 전달해야 합니다. 요약된 내용은 본문의 중요한 정보와 세부 사항을 최대한 담되, 중복된 내용이나 불필요한 설명은 제외하십시오.

        - 불필요한 내용: 일시적인 행사와 홍보 관련된 내용은 제외합니다.

        반환 형식은 JSON 형식으로 작성해주세요. 예시 형식은 다음과 같습니다:
        {json.dumps({
        "tags": ["태그1", "태그2", "태그3"],
        "score": 85,
        "relation_score": 30,
        "title": "원본 그대로의 문서 제목",
        "content": "본문에 대한 내용"
        })}
        문서:
        {doc_text}

        이와 같은 형식으로 JSON 형태로 반환해주세요.
        """

    def get_make_new_doc_prompt(self, compiled_doc):
        return f"""
        - 제공되는 문서를 이용해 새로운 문서를 작성해주세요. 
        - 문서의 내용은 딱딱하지 않게 밝고 친근한 말투로 설명하듯 작성합니다.
        - 새로운 문서는 여러개의 문단(content)로 이루어집니다.
        - 각 문서에서 중요한 제목(title), 부제(sub_title), 그리고 내용(content)을 추출하여 아래의 JSON 형식에 맞게 작성하세요.
        - 주제별 첫번째 문단은 제목과 부제목을 가집니다.
        - 제목에는 가능한 술의 이름을 넣지 않습니다.
        - 주제별 첫번째 문단을 제외하고는 제목과 부제목은 없을 수 있습니다.
        - 문단의 내용은 최소한 200자 이상이 되도록 합니다.
        - 각 내용은 요약하지 않고 정보를 깔끔하게 보여준다는 느낌으로 작성합니다.
        - 없는 내용을 창작하지 않습니다.
        - 일시적인 할인 행사 및 홍보 관련 내용은 반드시 제외합니다.
        - 내용에 대한 유형을 아래의 종류 중에서 골라서 하나만 지정합니다.
            type examples: history, tradition, culture, recommendation, cocktail_recipes, pairing, tasting, tip, production_process, other
        - JSON 형식으로 반환하며 이스케이프 처리가 될 수 있도록 합니다.
        - 내용에 큰따옴표가 있는 경우 작은따옴표로 변경합니다.

        반환되는 JSON 형식:
        {json.dumps({
        'contents': [
            {
                'seq': 1,
                'title': '문서의 주요 제목',
                'sub_title': '문서의 부제목',
                'content': '문서의 내용',
                'type': '내용의 유형'
            },
            {
                'seq': 2,
                'title': '두 번째 문서의 주요 제목',
                'sub_title': '두 번째 문서의 부제목',
                'content': '두 번째 문서의 내용',
                'type': '내용의 유형'
            }
        ]
        })}

        문서:
        {compiled_doc}
        """
