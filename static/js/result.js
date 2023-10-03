document.addEventListener("DOMContentLoaded", function() {
    
    
    $(".result_row").click(function(){
        var username=$("#user_id").val()
        state=$(this).find('td:eq(4)').text()
        if(state=="complete"){
            location.href=("/result/"+username+"/"+$(this).children('th').text())
        }
    })

})