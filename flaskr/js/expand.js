$(document).ready(function(){
   $(".read-more").click(function(){
       $(this).prev(".more").css({
           "max-height": "none",
           "overflow": "visible"
       });
   });
});

