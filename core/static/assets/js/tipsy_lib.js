

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