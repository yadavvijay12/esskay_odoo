$("#stryker_installation_form").hide();
$(function () {
        $("#ticket_type").change(function () {
        	if ($(this).val() == "select") {
                $("#stryker_fsm_form").hide();
                $("#stryker_installation_form").hide();
            } 
            if ($(this).val() == "stryker_fsm") {
                $("#stryker_fsm_form").show();
                $("#stryker_installation_form").hide();
            } 
            else if ($(this).val() == "stryker_installation") {
                $("#stryker_installation_form").show();
                $("#stryker_fsm_form").hide();
                }
        });
    });

$("#thermofisher_installation_form").hide();
$(function () {
        $("#ticket_type").change(function () {
        	if ($(this).val() == "select") {
                $("#thermofisher_fsm_form").hide();
                $("#thermofisher_installation_form").hide();
            } 
            if ($(this).val() == "thermofisher_fsm") {
                $("#thermofisher_fsm_form").show();
                $("#thermofisher_installation_form").hide();
            } 
            else if ($(this).val() == "thermofisher_installation") {
                $("#thermofisher_installation_form").show();
                $("#thermofisher_fsm_form").hide();
                }
        });
    });

$(document).ready(function($) {

	$(".login-btn-set-captha-stryker").click(function(event) {
		var recaptcha = $("#g-recaptcha-response").val();
		if (recaptcha === "") {
			event.preventDefault();
			document.getElementById('err').innerHTML="Please verify Captcha";
			event.preventDefault();
			event.stopImmediatePropagation();
			return false;
		}
		else{
			return true;
		}
	});

	$(".login-btn-set-captha-stryker-inst").click(function(event) {
		var recaptcha = $("#g-recaptcha-response").val();
		if (recaptcha === "") {
			event.preventDefault();
			document.getElementById('err').innerHTML="Please verify Captcha";
			event.preventDefault();
			event.stopImmediatePropagation();
			return false;
		}
		else{
			return true;
		}
	});

	$(".login-btn-set-captha-thermo").click(function(event) {
		var recaptcha = $("#g-recaptcha-response").val();
		if (recaptcha === "") {
			event.preventDefault();
			document.getElementById('err').innerHTML="Please verify Captcha";
			event.preventDefault();
			event.stopImmediatePropagation();
			return false;
		}
		else{
			return true;
		}
	});
});
