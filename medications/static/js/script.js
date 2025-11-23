
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

let shownNotifications = new Set();
let notificationCheckInterval = null;

function getCookie(name) {
    if (!document.cookie) return null;
    
    const cookie = document.cookie.split(';').find(c => 
        c.trim().startsWith(name + '=')
    );
    
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}

function requestNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }
}

function showBrowserNotification(notification) {
    if ("Notification" in window && Notification.permission === "granted" && 
        !shownNotifications.has(notification.id)) {
        
        const notif = new Notification("⏰ تذكير بالدواء", {
            body: `حان موعد دواء: ${notification.medication}\n${notification.notes || 'لا توجد ملاحظات'}`,
            tag: `reminder-${notification.id}`,
            requireInteraction: true,
            vibrate: [200, 100, 200]
        });
        
        notif.onclick = function() {
            window.focus();
            this.close();
            markAsDone(notification.id);
        };
        
        shownNotifications.add(notification.id);
    }
}

function addNotificationToDropdown(notification) {
    const dropdown = $('.dropdown-menu');
    
    if (dropdown.find(`[data-notification-id="${notification.id}"]`).length > 0) {
        return;
    }
    
    const item = `
        <li class="dropdown-item notification-item" data-notification-id="${notification.id}">
            <div class="notification-content">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <strong class="text-primary">${notification.medication}</strong>
                    <span class="badge bg-danger">جديد</span>
                </div>
                <p class="mb-1 text-muted small">⏰ ${notification.time}</p>
                ${notification.notes ? `<small class="text-secondary d-block mb-2">${notification.notes}</small>` : ''}
                <button class="btn btn-sm btn-success w-100 mark-done-btn" data-id="${notification.id}">
                    ✓ تم التناول
                </button>
            </div>
        </li>
    `;
    
    dropdown.find('.no-notifications').remove();
    dropdown.prepend(item);
}

function updateDropdownEmpty() {
    const dropdown = $('.dropdown-menu');
    if (dropdown.find('.notification-item').length === 0) {
        dropdown.html('<li class="dropdown-item no-notifications text-center text-muted py-3">لا توجد تذكيرات جديدة</li>');
    }
}

function updateBadge(count) {
    const badge = $('.badge-notification');
    count > 0 ? badge.text(count).show() : badge.hide();
}

function checkNotifications() {
    $.ajax({
        url: '/api/notifications/',
        type: 'GET',
        success: function(response) {            
            if (response.success && response.notifications.length > 0) {                
                response.notifications.forEach(notification => {
                    showBrowserNotification(notification);
                    addNotificationToDropdown(notification);
                });
                playNotificationSound();
            }
            updateBadgeCount();
        }
    });
}

function updateBadgeCount() {
    $.ajax({
        url: '/api/upcoming-reminders/',
        type: 'GET',
        success: function(response) {            
            if (response.success) {
                updateBadge(response.count);
                
                if (response.count > 0) {
                    response.reminders.forEach(addNotificationToDropdown);
                } else {
                    updateDropdownEmpty();
                }
            }
        }
    });
}

function markAsDone(reminderId) {    
    $.ajax({
        url: `/reminders/${reminderId}/mark-done/`,
        type: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function(response) {
            if (response.success) {                
                $(`.notification-item[data-notification-id="${reminderId}"]`).fadeOut(300, function() {
                    $(this).remove();
                    updateDropdownEmpty();
                });
                
                shownNotifications.delete(reminderId);
                updateBadgeCount();
                
                if ($('#medTable').length) {
                    $.get('/reminders/table/', html => $('#medTable').html(html));
                }
            }
        }
    });
}

function playNotificationSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);        
    } catch (e) {}
}

$(document).ready(function() {
    requestNotificationPermission();
    checkNotifications();
    updateBadgeCount();
    
    notificationCheckInterval = setInterval(checkNotifications, 30000);
});

$(document).on('click', '.mark-done-btn', function(e) {
    e.preventDefault();
    e.stopPropagation();
    markAsDone($(this).data('id'));
});

$(window).on('beforeunload', function() {
    if (notificationCheckInterval) {
        clearInterval(notificationCheckInterval);
    }
});