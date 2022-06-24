

const CONTENT_TYPE_LIQUOR   = 100;
const CONTENT_TYPE_COCKTAIL = 200;
const CONTENT_TYPE_INGD     = 300;
const CONTENT_TYPE_EQUIP    = 400;


function printSuccessPanel(title, message){
    swal(title, message, {
        icon : "success",
        buttons: {        			
            confirm: {
                className : 'btn btn-warning'
            }
        },
    });
}

function printWarningPanel(title, message){
    swal(title, message, {
        icon : "warning",
        buttons: {        			
            confirm: {
                className : 'btn btn-warning'
            }
        },
    });
}