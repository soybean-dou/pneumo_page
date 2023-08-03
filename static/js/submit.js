document.addEventListener("DOMContentLoaded", function() {
    

    $("#submit-btn").click(function(){
        var username="tmp"
        var jobname=$("#jobname").val();
        var wgstype = $('input[name=flexRadioDefault]:checked').val();
        var files = $("#file")[0].files
        
        console.log("done");

        var formData = new FormData();
        formData.append("username",username)
        formData.append("jobname", jobname);
        formData.append("wgstype", wgstype);
        for(var i=0; i<files.length;i++){
            formData.append("file", files[i]);
        }

        $.ajax({
            type:"POST",
            url: "/upload",
            processData: false,
            contentType: false,
            data: formData,
            success: function(rtn){
                const message = rtn.result;
                console.log("message: ", message)
                location.href=("/result/"+username)
            },
                err: function(err){
                console.log("err:", err.err)
            }
        })
    })

})