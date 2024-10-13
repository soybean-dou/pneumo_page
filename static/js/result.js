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
    $(".table").on("click", ".result_row", function () {
        var state = $(this).find('td:eq(4)').text();
        if (state == "complete") {
            location.href = ("/result/" + username + "/" + $(this).find('th').text());
        }
    });
    
    $(".table").on("click", ".del_job", function (event) {
        event.stopPropagation(); // 부모 요소의 클릭 이벤트가 발생하는 것을 방지
        var num = $(this).closest('.result_row').find('th').text();
        location.href = ("/result/" + username + "/" + num + "/delete");
    });
})