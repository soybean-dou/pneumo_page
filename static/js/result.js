document.addEventListener("DOMContentLoaded", function() {
    
    $(".result_row").each(function(){
        state=$(this).find('td:eq(3)').text()
        if(state=="complete"){
            $(this).css("cursor","pointer")
        }
    })


    var username=$("#user_id").text()
    $(".result_row").click(function(){
        state=$(this).find('td:eq(3)').text()
        if(state=="complete"){
            location.href=("/result/"+username+"/"+$(this).children('th').text())
        }
    })

})