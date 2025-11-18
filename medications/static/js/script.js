
(function () {
    "use strict";
    window.addEventListener('load', function () {
        var forms = document.getElementsByClassName("needs-validation");
        Array.prototype.forEach.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault(); 
                    event.stopPropagation();
                }
                form.classList.add("was-validated");
            }, false);
        });
    }, false);
})();

function ajaxRequest({url, method="POST", data=null, onSuccess, onError}) {
    $.ajax({
        url,
        type: method,
        data,
        headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
        success: res => onSuccess && onSuccess(res),
        error: xhr => onError ? onError(xhr) : alert("Unexpected error")
    });
}

function crudCreate({form, tableUrl, tableSelector, modalSelector}) {
    ajaxRequest({
        url: form.attr("action"),
        data: form.serialize(),
        onSuccess: function(res){
            if(res.success){
                $(modalSelector).modal("hide");
                $(tableSelector).load(tableUrl);
                form[0].reset();
            } else if(res.errors){
                showErrors(form, res.errors);
            }
        }
    });
}

function crudLoadEdit({url, modalSelector, contentSelector}) {
    ajaxRequest({
        url: url,
        method: "GET",
        onSuccess: function(html){
            $(contentSelector).html(html);
            new bootstrap.Modal(document.querySelector(modalSelector)).show();
        }
    });
}

function crudUpdate({form, tableUrl, tableSelector, modalSelector}) {
    ajaxRequest({
        url: form.attr("action"),
        data: form.serialize(),
        onSuccess: function(res){
            if(res.success){
                $(modalSelector).modal("hide");
                $(tableSelector).load(tableUrl);
            } else if(res.errors){
                showErrors(form, res.errors);
            }
        }
    });
}

function crudDelete({url, rowSelector, modalSelector, tableUrl, tableSelector}) {
    ajaxRequest({
        url: url,
        onSuccess: function(res){
            if(res.success){
                if(rowSelector)
                    $(rowSelector).remove();
                else
                    $(tableSelector).load(tableUrl);

                $(modalSelector).modal("hide");
            }
        }
    });
}

function showErrors(form, errors){
    let modal = form.closest(".modal-content");
    let msgBox = modal.find(".messages");

    if (!msgBox.length) {
        msgBox = $('<div class="messages"></div>');
        modal.prepend(msgBox);
    }

    let html = "";
    for (let key in errors){
        html += `<div class="alert alert-danger">${errors[key]}</div>`;
    }

    msgBox.html(html);
}

$(document).on('hidden.bs.modal', '.modal', function () {
    $(".modal-backdrop").remove();
    $("body").removeClass("modal-open");
});