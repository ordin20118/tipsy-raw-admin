

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