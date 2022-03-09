def imageIdToPath(id):

    idStr = str(id)
    idLen = len(idStr)

    # 빈자리 '0'으로 채움
    zeroStr = '0'
    if idLen < 9:   # 길이가 9보다 작은 경우
        zeroStr = '0' * (9 - idLen)
    else:           # 길이가 9이상인 경우
        zeroStr = '0' * (3 - (idLen%3))

    # 천의 자리까지 자름
    idStr = zeroStr + idStr
    idStr = idStr[0:-3] 

    # 3자리 단위로 '/' 추가
    path = ''
    for i in range(1, len(idStr)+1):
        path += idStr[i-1]
        if i%3 == 0 and i<len(idStr):
            path += '/'

    return path


def getScaledHeight(orgWidth, orgHeight, scaledWidth):
    
    ratio = float(orgHeight)/float(orgWidth)
    scaledHeight = int(scaledWidth * ratio)

    if scaledHeight == 0:
        scaledHeight = 1
        
    return scaledHeight


