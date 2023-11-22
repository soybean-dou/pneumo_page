document.addEventListener("DOMContentLoaded", function() {
    
    $(".job-type-radio").change(function(){
        if($(".job-type-radio:checked").attr("id")=="single-job"){
            $("#single-upload").show()
            $("#multiple-upload").hide()
        }
        else if($(".job-type-radio:checked").attr("id")=="multi-job"){
            $("#single-upload").hide()
            $("#multiple-upload").show()
        }
    })

    document.getElementById('upload_form').addEventListener('submit',function(event){
        const fileInput = document.getElementById('files');
        const jobname = document.getElementById('jobname');
        const login= document.getElementById('login')
        if(login!=null){            
            alert('Please sign in and try again!');
        }
        else{
            if(jobname.value.trim() == ""){
                event.preventDefault();            
                alert('Please enter your job name!');
            }
            else if (fileInput.files.length === 0) {
                event.preventDefault();            
                alert('Please select your input file!');
            }
            else{
                document.getElementById("btn-sub").style.display ='none';	
                document.getElementById("btn-lod").style.display ='inline-block';	
                document.getElementById("spinner").style.display ='inline-block';
            }
        }
    })

    document.getElementById('upload_multi_form').addEventListener('submit',function(event){
        const fileInput = document.getElementById('rawfiles');
        const login= document.getElementById('login')
        if(login!=null){            
            alert('Please sign in and try again!');
        }
        else{
            if (fileInput.files.length === 0) {
                event.preventDefault();            
                alert('Please select your input file!');
            }
            else{
                document.getElementById("btn-sub-m").style.display ='none';	
                document.getElementById("btn-lod-m").style.display ='inline-block';	
                document.getElementById("spinner-m").style.display ='inline-block';
            }
        }
    })

})