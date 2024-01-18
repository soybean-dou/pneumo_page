document.addEventListener("DOMContentLoaded", function() {
    
    $(".result_row").each(function(){
        state=$(this).find('td:eq(4)').text()
        if(state=="complete"){
            $(this).css("cursor","pointer")
            $(this).addClass("table-success")
        }
    })

    $('.result_row').hover(function(){
        state=$(this).find('td:eq(4)').text()
        if(state=="complete"){
            $(this).css('color','green');
        }
    },function(){
        $(this).css('color','black');
    });



    var username=$("#user_id").text()
    $(".result_row").click(function(){
        state=$(this).find('td:eq(4)').text()
        if(state=="complete"){
            location.href=("/result/"+username+"/"+$(this).children('th').text())
        }
    })

})