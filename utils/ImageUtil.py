import PIL.Image as pilimg
import os

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



