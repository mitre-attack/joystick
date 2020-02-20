function restRequest(type, data, callback) {
    $.ajax({
       url: '/rest',
       type: type,
       contentType: 'application/json',
       data: JSON.stringify(data),
       success:function(data) { callback(data); },
       error: function(xhr, ajaxOptions, thrownError) { console.log(thrownError); }
    });
}
