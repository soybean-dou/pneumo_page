document.addEventListener("DOMContentLoaded", function() {
    
    var username="tmp"
    $(".result_row").click(function(){
        state=$(this).find('td:eq(4)').text()
        if(state=="complete"){
            location.href=("/result/"+username+"/"+$(this).children('th').text())
        }
    })

})