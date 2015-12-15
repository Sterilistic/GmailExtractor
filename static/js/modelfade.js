$(function(){

$( "#bulkpop" ).on('show', function(){
    alert("Show!");
  $.ajax({
	type:"GET",
	url:"/download/download_mails/?label="+label_id,

});
});


});
