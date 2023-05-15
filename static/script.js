$(document).ready(function() {
  // get_response('Bonjour!');
  $('#message-form').on('submit', function(e) {
    e.preventDefault();
    var message = $('#message-input').val();
    if (message.trim() !== '') {
      $('#message-input').val('');
      add_message('user', message);
      get_response(message);
    }
  });

  $('#record-button').on('click', function() {
  var recordButton = $(this);
  var langToggleButton = $('#lang-toggle-button'); // Select the lang-toggle-button

  if (recordButton.hasClass('off')) {
    // Start recording
    recordButton.removeClass('btn-secondary off').addClass('btn-danger on');
    langToggleButton.removeClass('btn-secondary off').addClass('btn-danger on');
    $.post('/start_recording', {}, function(response) {
      console.log(response.message);  // Log the server's response
    });
  } else {
    // Stop recording and get the recorded text
    recordButton.removeClass('btn-danger on').addClass('btn-secondary off');
    langToggleButton.removeClass('btn-danger on').addClass('btn-secondary off');
    $.post('/end_recording', {}, function(response) {
      var recorded_text = response['recorded_text'];
      $('#message-input').val(recorded_text);
      $('#message-input').focus();
    });
  }
});


   $('#message-box').on('click', '.play-user-button', function() {
    var message = $(this).siblings('.card-body').text();
    $.post('/play_user_message', {'message': message}, function(response) {
      console.log(response);
    });
  });

  // $(document).keypress(function(e) {
  //   if (e.which == 114 || e.which == 82) { // 114 is 'r', and 82 is 'R'
  //     $('#record-button').click();
  //   }
  // });

  var darkMode = false;
  var languages = ['A', 'en', 'fr'];
  var currentLanguageIndex = 0;

  $('#mode-toggle-button').on('click', function() {
    darkMode = !darkMode;
    if (darkMode) {
      $('body').addClass('dark-mode');
      $('#mode-icon').removeClass('fa-moon').addClass('fa-sun');
    } else {
      $('body').removeClass('dark-mode');
      $('#mode-icon').removeClass('fa-sun').addClass('fa-moon');
    }
  });

  $('#lang-toggle-button').on('click', function() {
    currentLanguageIndex = (currentLanguageIndex + 1) % languages.length;
    $('#lang-text').text(languages[currentLanguageIndex]);
    $.post('/set_language', {'language': languages[currentLanguageIndex]}, function(response) {
      console.log(response.message);
    });
  });

  $('#dark-mode-button').on('click', function() {
    $('body').toggleClass('dark-mode');
  });

});

function add_message(sender, message) {
  var message_box = $('#message-box');
  var message_row = $('<div class="row mb-3"></div>');
  var message_col = $('<div class="col d-flex align-items-start"></div>');  // Changed to d-flex and align-items-start
  var message_card = $('<div class="card flex-grow-1"></div>');
  var message_body = $('<div class="card-body"></div>');
  message_body.text(message);

  if (sender === 'user') {
    message_card.addClass('bg-primary text-white');
    var img = $('<img src="/static/user.jpeg" class="profile-pic rounded-circle mr-3" width="50" height="50">');  // Replace path_to_user_image with the actual path
  } else {
    message_card.addClass('bg-light');
    var img = $('<img src="/static/bot.png" class="profile-pic rounded-circle mr-3" width="50" height="50">');  // Replace path_to_bot_image with the actual path
  }

  message_card.append(message_body);

  var button_container = $('<div class="button-container"></div>');
  if (sender === 'user') {
    var record_button = $('<div class="d-block"><button class="btn btn-link user-button play-user-button"><i class="fa-solid fa-user"></i></button></div>');
    button_container.append(record_button);
    var sound_on_button = $('<div class="d-block"><button class="btn btn-link user-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
    button_container.append(sound_on_button);
  } else {
    var sound_on_button = $('<div class="d-block"><button class="btn btn-link bot-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
    button_container.append(sound_on_button);
  }
  message_card.append(button_container);

  message_col.append(img).append(message_card);
  message_row.append(message_col);
  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  sound_on_button.on('click', function() {
    console.log('Sound on button clicked. Message:', message_body.text());
  });

  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  if (sender === 'user') {
    $.post('/store_message', {'sender': sender, 'message': message}, function (response) {
      if (response['status'] === 'success') {
        console.log('Message stored on the server-side');
      }
    });
  }
}

function toggleLoadingIcon(action) {
  $.post('/toggle_loading_icon', {action: action}, function(response) {
    if (response.action === 'show') {
      $('#not-loading-title').addClass('d-none');
      $('#not-loading-title').removeClass('d-flex');
      $('#loading-title').addClass('d-flex');
      $('#loading-title').removeClass('d-none');
    } else if (response.action === 'hide') {
      $('#not-loading-title').addClass('d-flex');
      $('#not-loading-title').removeClass('d-none');
      $('#loading-title').addClass('d-none');
      $('#loading-title').removeClass('d-flex');
    }
  });
}


function get_response(message) {
  toggleLoadingIcon('show');
  $.post('/get_response', {'message': message}, function(response) {
      var bot_message = response['message'];
      add_message('assistant', bot_message);
      get_next_message();
  });
}


function play_bot() {
  $.get('/play_bot', function(response) {});
}


function get_next_message() {
    $.get('/get_next_message', function(response) {
        var bot_message = response['message'];
        if (bot_message === null) {
            // No more messages to show
            toggleLoadingIcon('hide');
            play_bot();
            return;
        }
        update_last_message(bot_message);
        // Get the next message after a delay
        setTimeout(get_next_message, 0);  // Adjust the delay as needed
    });
}


function update_last_message(newContent) {
  var message_box = $('#message-box');
  var last_message_row = message_box.find('.row:last');
  var last_message_card_body = last_message_row.find('.card-body');
  last_message_card_body.text(newContent);
}


