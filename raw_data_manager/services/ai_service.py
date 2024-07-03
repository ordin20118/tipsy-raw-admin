import logging
from django.db import transaction
from core.openai_settings import OPENAI_SECRET_KEY, OPENAI_URL_PROMPT

from raw_data_manager.models import CrawledLiquor, CrawledLiquorTag, RawLiquor
import requests
import json

logger = logging.getLogger('django')

@transaction.atomic
def ana_description(crawled_liquor_id):
    # select liquor
    crawled_liquor = CrawledLiquor.objects.get(id=crawled_liquor_id)

    if crawled_liquor == None:
        return

    # request analyze to ChatGPT
    # 모델과 온도 설정
    model = "gpt-3.5-turbo"
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
    