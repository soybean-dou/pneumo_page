document.addEventListener("DOMContentLoaded", function() {
    
    var username=$("#user_id").text()
    $(".fastqc_download").click(function(){
        file_name=$(this).text()
        location.href=("/result/"+username+"/"+$(".result_row").children('th').text()+"/fastqc/"+file_name+"/download")
    })

})