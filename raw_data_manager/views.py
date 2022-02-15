from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from raw_data_manager.models import *
from raw_data_manager.serializers import *



def makeCategTree(parentId, treeKey, childDic, treeList):
    
    if len(treeKey) == 0:
        treeKey += str(parentId)
    else:
        treeKey += "^" + str(parentId)

    hasChild = False
    if parentId in childDic:
        hasChild = True
        
        tree = makeTreeInstance(treeKey)
        treeList.append(tree)
        # 또 자식 확인
        childs = childDic[parentId]
        for child in childs:
            makeCategTree(child.id, treeKey, childDic, treeList)
    else:
        tree = makeTreeInstance(treeKey)
        treeList.append(tree)

# make CategoryTree instance from category tree key
def makeTreeInstance(treeKey):
    tree = CategoryTree()
    tree.categ_tree_key = treeKey
    
    keys = treeKey.split('^')
    if len(keys) >= 1:
        tree.category1_id = keys[0]
    if len(keys) >= 2:
        tree.category2_id = keys[1]
    if len(keys) >= 3:
        tree.category3_id = keys[2]
    if len(keys) >= 4:
        tree.category4_id = keys[3]

    tree.reg_date = timezone.now()

    return tree

# 카테고리 트리 만들기
@api_view(['GET', 'POST'])
def categTree(request):
    
    if request.method == 'GET':
        # categTrees = CategoryTree.objects.all()	
        # serializer = CategoryTreeSerializer(categTrees, many=True) 
        # print(serializer.data)

        categTrees = CategoryTreeWithName.objects.raw('''
            SELECT 
                tree.*,
                categ1.name as category1_name,
                categ2.name as category2_name,
                categ3.name as category3_name,
                categ4.name as category4_name
            FROM tipsy_raw.category_tree tree
            LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON tree.category1_id = categ1.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON tree.category2_id = categ2.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON tree.category3_id = categ3.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON tree.category4_id = categ4.id
        ''')
        serializer = CategoryTreeWithNameSerializer(categTrees, many=True) 
        return Response(serializer.data)

    elif request.method == 'POST':
        
        categTrees = []
        totalCategs = RawCategory.objects.all()
    
        # make categ child dictionary
        categChilds = {}
        for categ in totalCategs:
            if categ.parent != -1:
                if categ.parent in categChilds:
                    categChilds[categ.parent].append(categ)
                else:
                    categChilds[categ.parent] = []
                    categChilds[categ.parent].append(categ)


        # 자식 확인 - 존재하면 해당 카테고리는 끝단x
        # 자식 반복
        # 자식의 자식 확인
        for categ in totalCategs:
            if categ.parent == -1:
                makeCategTree(categ.id, '', categChilds, categTrees)


        serializedTree = CategoryTreeSerializer(categTrees, many=True)

        # Update Data Example
        for tree in categTrees:
            tree.save()
        
        return Response(serializedTree.data)
        #return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 국가 데이터 API
@api_view(['GET'])
def country(request):
    
    if request.method == 'GET':
        allCountry = Country.objects.all()	
        serializer = CountrySerializer(allCountry, many=True) 
        
        # categTrees = CategoryTreeWithName.objects.raw('''
        #     SELECT 
        #         tree.*,
        #         categ1.name as category1_name,
        #         categ2.name as category2_name,
        #         categ3.name as category3_name,
        #         categ4.name as category4_name
        #     FROM tipsy_raw.category_tree tree
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON tree.category1_id = categ1.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON tree.category2_id = categ2.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON tree.category3_id = categ3.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON tree.category4_id = categ4.id
        # ''')
        # serializer = CategoryTreeWithNameSerializer(categTrees, many=True) 
        return Response(serializer.data)

    elif request.method == 'POST':
       pass 
       