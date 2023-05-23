$(document).ready(function() {
  $('#message-form').on('submit', function(e) {
    e.preventDefault();
    var message = $('#message-input').val();
    if (message.trim() !== '') {
      $('#message-input').val('');
      $.post('/user_message_info', {'message': message}, function(response) {
        var has_user_recording = response['user_recording'] !== null;
        var is_language_learning = response['is_language_learning'];
        add_message('user', message, has_user_recording, is_language_learning);
        get_response(message);
      });
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
      toggleLoadingIcon('show');
      $.post('/end_recording', {}, function(response) {
        var recorded_text = response['recorded_text'];
        $('#message-input').val(recorded_text);
        if (auto_send_recording) {
          $('#submit-button').click();
        } else {
          $('#message-input').focus();
        }
        toggleLoadingIcon('hide');
        });
      }
  });

  Mousetrap.bind('alt+r', function() {
    $('#record-button').click();
  });
  Mousetrap.bind('alt+l', function() {
    $('#lang-toggle-button').click();
  });
  var currentLanguageIndex = 0;

  // Check if the user's system prefers dark mode
  var prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  var darkMode = prefersDarkScheme.matches;

  // Set the initial dark mode state
  setDarkMode(darkMode);

  $('#mode-toggle-button').on('click', function() {
    darkMode = !darkMode;
    setDarkMode(darkMode);
  });

   $('#dark-mode-button').on('click', function() {
    $('body').toggleClass('dark-mode');
  });

  $.post('/set_language', {'language': languages[currentLanguageIndex]}, function(response) {
    console.log(response.message);
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

var message_counter = 1;
function add_message(sender, message, has_user_recording, is_language_learning) {
  var message_box = $('#message-box');
  var message_row = $('<div class="row mb-3"></div>');
  var message_col = $('<div class="col d-flex align-items-start"></div>');  // Changed to d-flex and align-items-start
  var message_card = $('<div class="card flex-grow-1"></div>');
  var message_body = $('<div class="card-body"></div>');
  message_body.text(message);
  message_body.id = "message_" + message_counter;
  message_counter += 1;

  if (sender === 'user') {
    message_card.addClass('bg-primary text-white');
    var img = $('<img src="' + user_profile_img + '" class="profile-pic rounded-circle mr-3" width="50" height="50">');  // Replace path_to_user_image with the actual path
  } else {
    message_card.addClass('bg-light');
    var img = $('<img src="' + bot_profile_img + '" class="profile-pic rounded-circle mr-3" width="50" height="50">');  // Replace path_to_bot_image with the actual path
  }

  message_card.append(message_body);

  var button_container = $('<div class="button-container"></div>');
  if (has_user_recording) {
    if (sender === 'user') {
      var record_button = $('<div class="d-block"><button class="btn btn-link user-button play-user-button"><i class="fa-solid fa-user"></i></button></div>');
    } else {
      var record_button = $('<div class="d-block"><button class="btn btn-link bot-button play-user-button"><i class="fa-solid fa-user"></i></button></div>');
    }
    button_container.append(record_button);
    record_button.on('click', function() {
    $.post('/play_user_recording', {'message_id': message_body.id}, function (response) {});
  });
  }
  if (sender === 'user') {
    if (is_language_learning) {
        var sound_on_button = $('<div class="d-block"><button class="btn btn-link user-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
        button_container.append(sound_on_button);
    } else {
        var sound_on_button = null;
    }
  } else {
    var translate_button = $('<div class="d-block"><button class="btn btn-link bot-button translate-button"><i class="fa fa-language"></i></button></div>');
    var sound_on_button = $('<div class="d-block"><button class="btn btn-link bot-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
    button_container.append(translate_button);
    button_container.append(sound_on_button);
    var translated_message = false;
    translate_button.on('click', function() {
      if (!translated_message) {
          $.post('/translate_text', {'text': message_body.text()}, function (response) {
              var translated_text = response['message'];
              var original_text = message_body.text();
              var combined_text = original_text + '<hr><em>' + translated_text + '</em>';
              translated_message = true;
              message_body.html(combined_text);
          });
      }
    });
  }
  message_card.append(button_container);

  message_col.append(img).append(message_card);
  message_row.append(message_col);
  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  if (sound_on_button !== null) {
    sound_on_button.on('click', function() {
      $.post('/play_bot_recording', {'message_id': message_body.id, 'text': message_body.text(), 'play_existing': 1}, function (response) {});
  });
  }

  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  if (sender === 'user') {
    $.post('/store_message', {'sender': sender, 'message': message}, function (response) {});
  }
}

function toggleLoadingIcon(action) {
    if (action === 'show') {
      $('#not-loading-title').addClass('d-none');
      $('#not-loading-title').removeClass('d-flex');
      $('#loading-title').addClass('d-flex');
      $('#loading-title').removeClass('d-none');
    } else if (action === 'hide') {
      $('#not-loading-title').addClass('d-flex');
      $('#not-loading-title').removeClass('d-none');
      $('#loading-title').addClass('d-none');
      $('#loading-title').removeClass('d-flex');
    }
}


function get_response(message) {
  toggleLoadingIcon('show');
  $.post('/get_response', {'message': message}, function(response) {
      var bot_message = response['message'];
      var message_index = response['message_index'];
      add_message('assistant', bot_message, false);
      get_next_message(message_index);
  });
}


function play_bot() {
  $.get('/play_bot', function(response) {});
}


function get_next_message(message_index) {
    $.post('/get_next_message', {'message_index': message_index}, function(response) {
        var bot_message = response['message'];
        if (bot_message === null) {
            // No more messages to show
            toggleLoadingIcon('hide');
            return;
        }
        update_last_message(bot_message);
        get_next_message(message_index)
    });
}


function update_last_message(newContent) {
  var message_box = $('#message-box');
  var last_message_row = message_box.find('.row:last');
  var last_message_card_body = last_message_row.find('.card-body');
  last_message_card_body.text(newContent);
}

function setDarkMode(isDarkMode) {
    if (isDarkMode) {
      $('body').addClass('dark-mode');
      $('#mode-icon').removeClass('fa-moon').addClass('fa-sun');
    } else {
      $('body').removeClass('dark-mode');
      $('#mode-icon').removeClass('fa-sun').addClass('fa-moon');
    }
  }

function getCurrentTime() {
  var now = new Date();

  var year = now.getFullYear();
  var month = String(now.getMonth() + 1).padStart(2, '0');
  var day = String(now.getDate()).padStart(2, '0');
  var hours = String(now.getHours()).padStart(2, '0');
  var minutes = String(now.getMinutes()).padStart(2, '0');
  var seconds = String(now.getSeconds()).padStart(2, '0');

  var formattedTime = year + '-' + month + '-' + day + '_' + hours + ':' + minutes + ':' + seconds;
  return formattedTime;
}