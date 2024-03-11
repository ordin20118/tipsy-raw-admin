import PIL.Image as pilimg
import os
import tempfile
import boto3
import uuid
import hashlib
import base64
import core.s3_settings as s3_settings

def imageIdToPath(id):

    idStr = str(id)
    idLen = len(idStr)

    # 빈자리 '0'으로 채움
    zeroStr = '0'
    if idLen < 9:   # 길이가 9보다 작은 경우
        zeroStr = '0' * (9 - idLen)
    else:           # 길이가 9이상인 경우
        zeroStr = ''
        #zeroStr = '0' * (3 - (idLen%3))

    print(zeroStr)

    # 천의 자리까지 자름
    idStr = zeroStr + idStr

    print(idStr)

    idStr = idStr[0:-3] 
    print(idStr)

    # 3자리 단위로 '/' 추가
    path = ''
    for i in range(1, len(idStr)+1):
        path += idStr[i-1]
        if i%3 == 0 and i<len(idStr):
            path += '/'

    path = path[0:7]
    return path

# TEST
# path = imageIdToPath(1234)
# print(path)
# print("\n\n")

# path = imageIdToPath(123456)
# print(path)
# print("\n\n")

# path = imageIdToPath(123123999777)
# print(path)

def getScaledHeight(org_width, org_height, scaled_width):
    
    ratio = float(org_height)/float(org_width)
    scaled_height = int(scaled_width * ratio)

    if scaled_height == 0:
        scaled_height = 1
        
    return scaled_height


# 이미지 ID를 이용해 경로를 생성하고 지정된 디렉토리로 저장
# 지정된 디렉토리 이후의 경로를 반환
# param -image_file : 이미지 파일 객체
# param -image_id : 이미지의 DB ID
# param -dir_path : 이미지를 저장할 로컬 디렉토리 경로
def saveImgToPath(image_file, image_id, img_dir):

    try:
        # 3. 원본, 300, 600 3가지로 저장          
        # - 파일 형식: image/{이미지 경로}/{이미지_ID}_{이미지_SIZE}.png
        # 업로드할 이미지 데이터 pillow로 객체화
        img = pilimg.open(image_file)

        # 저장할 경로 폴더 존재 확인
        if os.path.isdir(img_dir) == False:
            os.makedirs(img_dir)
        
        imgOrgPath = img_dir + str(image_id) + '.' + 'png'
        
        img.save(imgOrgPath)

        # resize 300
        img300Path = img_dir + str(image_id) + '_300.' + 'png'
        height_300 = getScaledHeight(img.width, img.height, 300)

        img300 = img.resize((300, height_300))
        img300.save(img300Path)

        # resize 600
        img600Path = img_dir + str(image_id) + '_600.' + 'png'
        height_600 = getScaledHeight(img.width, img.height, 600)
        
        img600 = img.resize((600, height_600))
        img600.save(img600Path)
    except Exception as e: 
         print('[save image to path error]', e)
         raise


# AWS S3에 이미지 저장
# 저장된 s3 key 반환
# param -image_file : 이미지 파일 객체
# param -s3_path : 이미지를 저장할 s3 경로
def saveImgToS3(image_file, path, ext = None):
    try:
        # s3 client 연결
        s3_client = boto3.resource('s3', aws_access_key_id=s3_settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=s3_settings.AWS_SECRET_ACCESS_KEY)

        # 확장자 얻기
        img = None
        if isinstance(image_file, pilimg.Image):
            img = image_file
        else:
            img = pilimg.open(image_file)
        
        if img.format is None and ext is None:
            raise Exception('Can\'t findl image\'s extension.' )
        elif img.format is not None:
            extension = img.format.lower()
        else:
            extension = ext

        # 랜덤 키 생성
        random_key = uuid.uuid1().hex
        s3_key = path + '/' + random_key + '.' + extension

        # 임시 파일 저장
        temp_path = ''
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_path = temp_file.name
            # PIL을 사용하여 이미지 저장
            img.save(temp_path, format=extension)

        # 파일 데이터 가져오기
        data = open(temp_path,'rb')

        # form에서 받은 image 파일을 그대로 전송 시 MD5에러 발생
        # => 로컬에 임시 저장 후 전송
        s3_client.Bucket(s3_settings.AWS_S3_BUCKET_NAME).put_object( 
            Key=s3_key, 
            Body=data, 
            ContentType=extension)
        
        os.remove(temp_path)
        return s3_key

    except Exception as e: 
         print('[save image to s3 error]', e)
         raise


def deleteObjectFromS3(s3_key):
    try:
        # s3 client 연결
        s3_client = boto3.resource('s3', aws_access_key_id=s3_settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=s3_settings.AWS_SECRET_ACCESS_KEY)

        # S3 버킷 이름과 객체 키를 지정하여 객체 제거
        s3_client.Bucket(s3_settings.AWS_S3_BUCKET_NAME).delete_objects(
            Delete={
                'Objects': [
                    {'Key': s3_key}
                ],
                'Quiet': False  # 실패한 객체 삭제 여부 설정 (True: 실패 시 메시지 없음, False: 실패 시 메시지 출력)
            }
        )

        print(f'Successfully deleted object: {s3_key}')
    
    except Exception as e:
        print(f'Error deleting s3 object: {e}')


def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while chunk := f.read(8192):
            md5.update(chunk)
    return base64.b64encode(md5.digest()).decode('utf-8')

