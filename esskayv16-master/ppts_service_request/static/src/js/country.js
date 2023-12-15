odoo.define('ppts_service_request.state_id_update', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    // SR FSM
    // DEFAULT TRIGGERED STATE
    var country = $('#customer_country_id').val();
    $("#customer_country_id").val(country).trigger("change");
    $('#customer_country_id').on('change', function() {
        var country = $('#customer_country_id').val();
        $("#customer_state_id option").remove();
        ajax.jsonRpc("/update_state_id", 'call', {
                'country': country
            })
            .then(function(data) {
                console.log(data)
                for (var i = 0; i < data.state_domain.length; i++) {
                    var vals = data.state_domain[i].id
                    var state_name = data.state_domain[i].value
                    $("#customer_state_id").append($("<option></option>").attr("value", vals).text(state_name));
                }

            });

    });
    // ONCHANGE TRIGGERED STATE
    $(document).ready(function() {
        var country = $('#customer_country_id').val();
        console.log(country)
        $("#customer_state_id option").remove();
        ajax.jsonRpc("/update_state_id", 'call', {
                'country': country
            })
            .then(function(data) {
                console.log(data)
                for (var i = 0; i < data.state_domain.length; i++) {
                    var vals = data.state_domain[i].id
                    var state_name = data.state_domain[i].value
                    $("#customer_state_id").append($("<option></option>").attr("value", vals).text(state_name));
                }

            });

    });


    // SR INSTALLATION
    var country = $('#sr_inst_country_id').val();
    $("#sr_inst_country_id").val(country).trigger("change");
    $('#sr_inst_country_id').on('change', function() {
        var country = $('#sr_inst_country_id').val();
        $("#sr_inst_state_id option").remove();
        ajax.jsonRpc("/update_state_id", 'call', {
                'country': country
            })
            .then(function(data) {
                console.log(data)
                for (var i = 0; i < data.state_domain.length; i++) {
                    var vals = data.state_domain[i].id
                    var state_name = data.state_domain[i].value
                    $("#sr_inst_state_id").append($("<option></option>").attr("value", vals).text(state_name));
                }

            });

    });

    $(document).ready(function() {
        var country = $('#sr_inst_country_id').val();
        console.log(country)
        $("#sr_inst_state_id option").remove();
        ajax.jsonRpc("/update_state_id", 'call', {
                'country': country
            })
            .then(function(data) {
                console.log(data)
                for (var i = 0; i < data.state_domain.length; i++) {
                    var vals = data.state_domain[i].id
                    var state_name = data.state_domain[i].value
                    $("#sr_inst_state_id").append($("<option></option>").attr("value", vals).text(state_name));
                }

            });

    });
});