$(document).ready(function(){
	$("body").bind("dragenter dragover drop", function(event){
		event.stopPropagation();
		event.preventDefault();
	});
	
	$("#dropzone").bind("drop", function(event){
		event.stopPropagation();
		event.preventDefault();
		
		upload(event.originalEvent.dataTransfer.files[0]);
	});
	
	$("#fileselector").click(function(){
		$("#uploader").click();
	});
	
	$("#uploader").change(function(){
		upload($("#uploader")[0].files[0]);
	});
	
	$("#uploadform").submit(function(event){
		event.preventDefault();
		
		return false;
	});
	
	if($("#message_text").text() != "")
		message($("#message_text").text());
	
	$.img = new Object();
	$.img.settings = new Object();
});

function uploadStartUI(image) {
	$("#message p").text("");
	$("#message").css("visibility", "hidden");
	
	$("#dropzone").off("drop");
	$("#uploaddetails").css("opacity", "0.0");
	$("#uploaddetails").css("display", "none");
	$("#dropzone").css("max-width", "70%");
	$("#dropzone").css("border-radius", "10px");
	$("#settings").css("left", "72%");
	$("#settings").css("visibility", "visible");
	
	
	$("input[name=days_before_delete]").click(function(e){
		e.stopPropagation();
		e.preventDefault();
		
		$("#enable_day_delete").prop("checked", true);
	});
	
	$("input[name=views_before_delete]").click(function(e){
		e.stopPropagation();
		e.preventDefault();
		
		$("#enable_view_delete").prop("checked", true);
	});
	
	$("input[name=inactive_days_before_delete]").click(function(e){
		e.stopPropagation();
		e.preventDefault();
		
		$("#enable_inactive_delete").prop("checked", true);
	});
	
	var prev = document.getElementById("preview");
	prev.src = window.URL.createObjectURL(image);
	prev.onload = function(){
		window.URL.revokeObjectURL(this.src);
	};
	$("#preview_container").css("opacity", "0.5");
	$("#imagespinner").css("visibility", "visible");
}

function uploadCompleteUI(data) {
	$("#image_url")[0].disabled = false;
	$("input[type=text]").focus(function(){
		$(this).select(); 
	});
	$("#image_url").select();
	$("#image_url").val(data.url);

	$("#delete_url")[0].disabled = false;
	$("#delete_url").val(data.delete_url);

  
	$("#preview_container").css("opacity", "1.0");
	$("#imagespinner").css("visibility", "hidden");
}

function upload(image) {
	var formData = new FormData($("#uploadform"))
	formData.append("uploader", image)
	
	if(!image.type.match(/^image\//))
	{
		error("Images only, please.");
		return false;
	}
	
	if(image.size > (1024 * 1024 * 2))
	{
		error("Max size 2MB.");
		return false;
	}
	
	uploadStartUI(image);
	
	$.ajax({
		url: '/upload',
		type: 'POST',
		data: formData,
		async: true,
		cache: false,
		contentType: false,
		processData: false,
		success: function (returndata) {
			var data = $.parseJSON(returndata);
			uploadCompleteUI(data);
			enableSettings(data);
			sendSettings();
		}
	});
}

function updateSettings() {
	if(!$("#enable_day_delete").prop('checked'))
		$.img.settings.expires = null;
	else
		$.img.settings.expires = $("input[name=days_before_delete]").val() * 24 * 60 * 60;
	
	if(!$("#enable_view_delete").prop('checked'))
		$.img.settings.view_limit = null;
	else
		$.img.settings.view_limit = $("input[name=views_before_delete]").val();
	
	if(!$("#enable_inactive_delete").prop('checked'))
		$.img.settings.inactive_expiry = null;
	else
		$.img.settings.inactive_expiry = $("input[name=inactive_days_before_delete]").val() * 24 * 60 * 60;
}

function sendSettings() {
	if(!$.img.token || Object.keys($.img.settings).length == 0)
		return;
	
	$("#settingsspinner").css("visibility", "visible");
	$("#checkmark").css("visibility", "hidden");

	$("#settingsform").off("mouseleave");
	
	var formData = new FormData()
	
	formData.append("view_limit", $.img.settings.view_limit);
	formData.append("expires", $.img.settings.expires);
	formData.append("inactive_expiry", $.img.settings.inactive_expiry);
	formData.append("token", $.img.token)
	
	$.ajax({
		url: '/update',
		type: 'POST',
		data: formData,
		async: true,
		cache: false,
		contentType: false,
		processData: false,
		success: function (returndata) {
			var data = $.parseJSON(returndata);
					
			$("#settingsspinner").css("visibility", "hidden");
			$("#checkmark").css("visibility", "visible");
			
			if($.img.token != null)
				enableSettings(data);
		}
	});
}

function enableSettings(data) {
	if(data.token)
		$.img.token = data.token;
	
	$.img.settings = new Object();
	$("#settingsform").bind("mouseleave", function(e){
		//important because of fuckery
		$("input[name=days_before_delete]").blur();
		$("input[name=views_before_delete]").blur();
		$("input[name=inactive_days_before_delete]").blur();
		
		sendSettings();
	});
}

function message(mess) {
	//$("#message").removeClass("error");
	$("#message p").text(mess);
	$("#message").css("visibility", "visible");
}

function error(err) {
	$("#message").addClass("error");
	$("#message p").text(err);
	$("#message").css("visibility", "visible");
}