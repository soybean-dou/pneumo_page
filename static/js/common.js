document.addEventListener("DOMContentLoaded", function() {
    
    user_id=$("#user_id").text()
    $("#nav-result").attr("href","/result/"+user_id)
    
    $('.nav-link').click(function (e) {
        var href = $(this).attr("href");
        var targetTop = $(href).offset().top-100;
        $("#detail_data").stop().animate({ scrollTop : targetTop }, 300);
        e.preventDefault();
     });

     function Page__updateIndicatorActive() {
        var scrollTop = $(window).scrollTop();
       // 스크롤 
        $($(".section").get().reverse()).each(function (index, node) {
           var offsetTop = parseInt($(this).attr("data-offset-top"));
           if (scrollTop >= offsetTop) { 
              $(".nav-link.active").removeClass("active");
              var currentPageIndex = $(this).index();
              $(".nav-link").eq(currentPageIndex).addClass("active");
              $("#detail_data").attr("data-current-page-index", currentPageIndex);
              return false;
           }
        });
     }

     function Page__updateOffsetTop() {    
        $(".section").each(function (index, node) {
             var $page = $(node);
             var offsetTop = $page.offset().top - 60;
             $page.attr("data-offset-top", offsetTop);
        });    
        Page__updateIndicatorActive();
    }
})