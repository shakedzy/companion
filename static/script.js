$(document).ready(function() {
  $('#message-form').on('submit', function(e) {
    e.preventDefault();
    var message = $('#message-input').val();
    if (message.trim() !== '') {
      $('#message-input').val('');
      add_message('You', message);
      get_response(message);
    }
  });

  $('#record-button').on('click', function() {
    $.post('/record_message', {}, function(response) {
      var recorded_text = response['recorded_text'];
      $('#message-input').val(recorded_text);
      $('#message-input').focus();
    });
  });

  var socket = io.connect(location.origin);
  socket.on('loading_icon', function(data) {
    if (data.status === 'show') {
      $('#loading-icon').css('display', 'inline-block');
    } else if (data.status === 'hide') {
      $('#loading-icon').css('display', 'none');
    }
  });

  // socket.on('bot_message', function(data) {
  //   add_message('Bot', data.message);
  // });
});

function add_message(sender, message) {
  var message_box = $('#message-box');
  var message_row = $('<div class="row mb-3 align-items-center"></div>');
  var message_col = $('<div class="col"></div>');
  var message_card = $('<div class="card"></div>');
  var message_body = $('<div class="card-body"></div>');
  message_body.text(message);

  if (sender === 'You') {
    message_card.addClass('bg-primary text-white');
  } else {
    message_card.addClass('bg-light');
  }

  message_card.append(message_body);
  message_col.append(message_card);
  message_row.append(message_col);

  // Add the "Sound on" button for both user and bot messages
  var button_col = $('<div class="col-auto"></div>');
  var button = $('<button class="btn btn-sm btn-link"><i class="fas fa-volume-up"></i></button>');
  button_col.append(button);
  message_row.append(button_col);

  button.on('click', function() {
    console.log('Sound on button clicked. Message:', message_body.text());
  });

  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  $.post('/store_message', {'sender': sender, 'message': message}, function(response) {
    if (response['status'] === 'success') {
      console.log('Message stored on the server-side with ID:', response['message_id']);
    }
  });
}

function toggleLoadingIcon(action) {
  $.post('/toggle_loading_icon', {action: action}, function(response) {
    if (response.action === 'show') {
      $('#loading-icon').removeClass('d-none');
    } else if (response.action === 'hide') {
      $('#loading-icon').addClass('d-none');
    }
  });
}


function get_response(message) {
  $.post('/get_response', {'message': message}, function(response) {
    var messages = response['messages'];
    var delay = 0;
    var fullMessage = '';

    messages.forEach(function(bot_message, index) {
      setTimeout(function() {
        fullMessage += bot_message;
        if (index < messages.length - 1) {
          fullMessage += ' ';
        }
        if (index === 0) {
          add_message('Bot', fullMessage);
        } else {
          update_last_message(fullMessage);
        }
      }, delay);
      delay += 1000;  // Adjust the delay between message parts as needed
    });
  });
}


function update_last_message(newContent) {
  var message_box = $('#message-box');
  var last_message_row = message_box.find('.row:last');
  var last_message_card_body = last_message_row.find('.card-body');
  last_message_card_body.text(newContent);
}


