document.addEventListener("DOMContentLoaded", function() {
    
    var username=$("#user_id").text()
    $(".fastqc_download").click(function(){
        file_name=$(this).text()
        location.href=("/result/"+username+"/"+$(".result_row").children('th').text()+"/fastqc/"+file_name+"/download")
    })

    $(".gene_anot_download").click(function(){
        file_name=$(this).text()
        location.href=("/result/"+username+"/"+$(".result_row").children('th').text()+"/gene_anot/download")
    })

    $(".assembled_download").click(function(){
        file_name=$(this).text()
        location.href=("/result/"+username+"/"+$(".result_row").children('th').text()+"/assembled_fasta/download")
    })

    $(".toggle").click(function(){
        if($(this).text()=="▼"){
            $(this).text($(this).text().replace("▼","▲"));
        }else if($(this).text()=="▲"){
            $(this).text($(this).text().replace("▲","▼"));
        }
        
    })
    
})