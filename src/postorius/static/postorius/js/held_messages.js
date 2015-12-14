var loadjs = function(rest_url, error_message) {
  $('#all-messages-checkbox').change(function() {
    $('.message-checkbox').prop('checked', this.checked);
  });
  $('.show-modal-btn').click(function() {
    var msgid = $(this).data('msgid');
    $.ajax({
      url: rest_url + msgid,
      success: function(data) {
        $('#msg-title').html(data.subject);
        $('.modal-footer form input[name="msgid"]').attr('value', msgid);
        $('#held-stripped-message').html(data.stripped_msg.body.replace(/\n/g, "<br />"));
        $('#held-full-message').html(data.msg.replace(/\n/g, "<br />"));
        $('#held-messages-modal').modal('show');
      },
      error : function() {
        alert(error_message);
      },
      statusCode: {
        500: function() {
          alert(error_message);
        }
      }});
    return false;
  });
  $('#toggle-full-message').click(function() {
    if ($(this).hasClass('active')) {
      $('#held-stripped-message').removeClass('hidden');
      $('#held-full-message').addClass('hidden');
    } else {
      $('#held-stripped-message').addClass('hidden');
      $('#held-full-message').removeClass('hidden');
    }
  });
  $('#held-messages-modal').on('hidden.bs.modal', function() {
    $('#held-stripped-message').removeClass('hidden');
    $('#held-full-message').addClass('hidden');
    $('#msg-title').html('');
    $('#toggle-full-message').removeClass('active');
  });
}
