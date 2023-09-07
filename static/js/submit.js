document.addEventListener("DOMContentLoaded", function() {
    
    $("#logout")

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

})