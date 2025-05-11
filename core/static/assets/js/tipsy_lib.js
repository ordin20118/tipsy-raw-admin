const COCKTAIL_FORMAT_VERSION = 0.1;

const CONTENT_TYPE_LIQUOR = 100;
const CONTENT_TYPE_COCKTAIL = 200;
const CONTENT_TYPE_INGD = 300;
const CONTENT_TYPE_EQUIP = 400;
const CONTENT_TYPE_WORD = 500;

function printSuccessPanel(title, message) {
    swal(title, message, {
        icon: "success",
        buttons: {
            confirm: {
                className: "btn btn-success",
            },
        },
    });
}

function printWarningPanel(title, message) {
    swal(title, message, {
        icon: "warning",
        buttons: {
            confirm: {
                className: "btn btn-warning",
            },
        },
    });
}

function printDangerPanel(title, message) {
    swal(title, message, {
        icon: "error",
        buttons: {
            confirm: {
                className: "btn btn-danger",
            },
        },
    });
}

function loadCategTree() {
    var url = "/raw_data_manager/api/categ_tree";

    $.ajax({
        url: url,
        type: "get",
        success: function (data) {
            //console.log(data);
            if (data.length > 0) {
                categTree = data;

                // 변수 설정
                for (var categ of data) {
                    //console.log(categ)
                    // '^'을 기준으로 split
                    // 깊이에 따라서 부모 설정
                    var treeStr = categ["categ_tree_key"];
                    splitedArr = treeStr.split("^");

                    if (splitedArr.length > 0) {
                        for (var i = 1; i <= splitedArr.length; i++) {
                            if (i == 1) {
                                var info = {
                                    id: categ["category1_id"],
                                    parent: -1,
                                    name: categ["category1_name"],
                                };
                                categLv1.set(info["id"], info);
                                categMap.set(info["id"], info);
                            } else if (i == 2) {
                                var info = {
                                    id: categ["category2_id"],
                                    parent: categ["category1_id"],
                                    name: categ["category2_name"],
                                };

                                if (categMap.get(info["id"]) == null) {
                                    if (categLv2Parent.get(info["parent"]) != null) {
                                        // parent가 등록되어 있으면 기존의 리스트에 추가
                                        var childList = categLv2Parent.get(info["parent"]);
                                        childList.push(info);
                                        categLv2Parent.set(info["parent"], childList);
                                    } else {
                                        // parent가 등록되어 있지 않으면 새로 리스트 생성해서 넣기
                                        var newChildList = new Array();
                                        newChildList.push(info);
                                        categLv2Parent.set(info["parent"], newChildList);
                                    }
                                    categMap.set(info["id"], info);
                                }
                            } else if (i == 3) {
                                var info = {
                                    id: categ["category3_id"],
                                    parent: categ["category2_id"],
                                    name: categ["category3_name"],
                                };

                                if (categMap.get(info["id"]) == null) {
                                    if (categLv3Parent.get(info["parent"]) != null) {
                                        // parent가 등록되어 있으면 기존의 리스트에 추가
                                        var childList = categLv3Parent.get(info["parent"]);
                                        childList.push(info);
                                        categLv3Parent.set(info["parent"], childList);
                                    } else {
                                        // parent가 등록되어 있지 않으면 새로 리스트 생성해서 넣기
                                        var newChildList = new Array();
                                        newChildList.push(info);
                                        categLv3Parent.set(info["parent"], newChildList);
                                    }
                                    categMap.set(info["id"], info);
                                }
                            } else if (i == 4) {
                                var info = {
                                    id: categ["category4_id"],
                                    parent: categ["category3_id"],
                                    name: categ["category4_name"],
                                };

                                if (categMap.get(info["id"]) == null) {
                                    if (categLv4Parent.get(info["parent"]) != null) {
                                        // parent가 등록되어 있으면 기존의 리스트에 추가
                                        var childList = categLv4Parent.get(info["parent"]);
                                        childList.push(info);
                                        categLv4Parent.set(info["parent"], childList);
                                    } else {
                                        // parent가 등록되어 있지 않으면 새로 리스트 생성해서 넣기
                                        var newChildList = new Array();
                                        newChildList.push(info);
                                        categLv4Parent.set(info["parent"], newChildList);
                                    }
                                    categMap.set(info["id"], info);
                                }
                            }
                        }
                    }
                }

                printCategSelect(0);
            }
        },
        error: function (request, status, error) {},
    });
}

function printCategSelect(selLv) {
    let noneItem = "<option value=0>선택 없음</option>";

    if (selLv == 0) {
        initCategSelect(1);
        categLv1.forEach(function (value, key) {
            let categ = value;
            let item = "<option value=" + categ["id"] + ">" + categ["name"] + "</option>";
            $("#categ1Select").append(item);
        });
    } else if (selLv == 4) {
        return;
    }

    // 카테고리 레벨1 선택되었을 때
    if (selLv == 1) {
        initCategSelect(2);

        if ($("#categ1Select").val() != "0") {
            let parentId = Number($("#categ1Select").val());

            if (categLv2Parent.get(parentId) != null) {
                let childList = categLv2Parent.get(parentId);
                childList.forEach(function (categ) {
                    let item = "<option value=" + categ["id"] + ">" + categ["name"] + "</option>";
                    $("#categ2Select").append(item);
                });
            }
        }
    }

    // 카테고리 레벨2 선택되었을 때
    if (selLv == 2) {
        initCategSelect(3);

        if ($("#categ2Select").val() != "0") {
            let parentId = Number($("#categ2Select").val());

            if (categLv3Parent.get(parentId) != null) {
                let childList = categLv3Parent.get(parentId);
                childList.forEach(function (categ) {
                    let item = "<option value=" + categ["id"] + ">" + categ["name"] + "</option>";
                    $("#categ3Select").append(item);
                });
            }
        }
    }

    // 카테고리 레벨3 선택되었을 때
    if (selLv == 3) {
        initCategSelect(4);

        if ($("#categ3Select").val() != "0") {
            let parentId = Number($("#categ3Select").val());

            if (categLv4Parent.get(parentId) != null) {
                let childList = categLv4Parent.get(parentId);
                childList.forEach(function (categ) {
                    let item = "<option value=" + categ["id"] + ">" + categ["name"] + "</option>";
                    $("#categ4Select").append(item);
                });
            }
        }
    }
    isLoadedCateg = true;
}

function initCategSelect(level) {
    let noneItem = "<option value=0>선택 없음</option>";
    let count = 0;
    for (var i = level; count <= 5 - level; i++, count++) {
        $("#categ" + i + "Select").empty();
        $("#categ" + i + "Select").append(noneItem);
    }
}

// 국가 데이터 load
var countryList = [];
function loadCountryData() {
    var url = "/raw_data_manager/api/country";

    $.ajax({
        url: url,
        type: "get",
        success: function (data) {
            //console.log(data);
            if (data.length > 0) {
                printCountry(data);
            }
            //  else{
            // 	alert(getErrorMsg(data['state']));
            // }
        },
        error: function (request, status, error) {},
    });
}

function printCountry(data) {
    countryList = data;

    $("#country").empty();
    var defaultOption = '<a class="dropdown-item" href="javascript:selectCountry(0)">국가 선택</a>';
    $("#country").append(defaultOption);

    for (var i = 0; i < countryList.length; i++) {
        var country = countryList[i];
        var option =
            '<a class="dropdown-item" href="javascript:selectCountry(' +
            country["country_id"] +
            ')"><img src="' +
            country["image"] +
            '" style="width: 30px; margin: 0px 9px 0px 0px;">' +
            country["name"] +
            "</a>";

        $("#country").append(option);
    }
    isLoadedCountry = true;
}

function selectCountry(id) {
    if (id == 0) {
        $("#countrySelectButton").html("국가 선택");
        // 선택된 아이디 설정
        selCountry = id;
        return;
    }

    for (var i = 0; i < countryList.length; i++) {
        if (countryList[i]["country_id"] == id) {
            // 텍스트 설정
            $("#countrySelectButton").html(
                '<img src="' +
                    countryList[i]["image"] +
                    '" style="width: 30px; margin: 0px 9px 0px 0px;">' +
                    countryList[i]["name"]
            );
            // 선택된 아이디 설정
            selCountry = id;
        }
    }
}
