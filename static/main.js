$.getScript("/static/common.js");
$.getScript("/static/audio.js");

$(document).ready(function() {
  var currentLanguageIndex = 0;

  // Check if the user's system prefers dark mode
  var prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  var darkMode = prefersDarkScheme.matches;

  var textarea = document.getElementById('message-input');
  textarea.addEventListener('input', function(e) {
      autoResize(this);
  });
  autoResize(textarea);

  $('#message-form').on('submit', function(e) {
    e.preventDefault();
    var message = $('#message-input').val();
    if (message.trim() !== '') {
      $('#message-input').val('');
      $.post('/user_message_info', {'message': message}, function(response) {
        var has_user_recording = response['user_recording'] !== null;
        var is_language_learning = response['is_language_learning'];
        var error_message = response['error'];
        if (error_message !== null) {
            showNotification(error_message);
        }
        addMessage('user', message, has_user_recording, is_language_learning);
        getResponse(0);
      });
    }
  });

  let recordedBlobPromise;
  $('#record-button').on('click', function() {
    var recordButton = $(this);
    var langToggleButton = $('#lang-toggle-button'); // Select the lang-toggle-button

    if (recordButton.attr('name') === 'stop') {
        stopAudio();
    }
    else if (recordButton.hasClass('off')) {
      // Start recording
      recordButton.removeClass('btn-secondary off').addClass('btn-danger on');
      langToggleButton.removeClass('btn-secondary off').addClass('btn-danger on');
      recordedBlobPromise = startRecording();
    } else {
      // Stop recording and get the recorded text
      recordButton.removeClass('btn-danger on').addClass('btn-secondary off');
      langToggleButton.removeClass('btn-danger on').addClass('btn-secondary off');
      toggleLoadingIcon('show');
      stopRecording();
      recordedBlobPromise.then(blob => {
          uploadAudio(blob).then(filename => {
              $.post('/transcribe_recording', {'filename': filename}, function(response) {
                  var recorded_text = response['recorded_text'];
                  var error_message = response['error'];
                  if (error_message !== null) {
                      showNotification(error_message);
                  }
                  $('#message-input').val(recorded_text);
                  if (auto_send_recording) {
                    $('#submit-button').click();
                  } else {
                    $('#message-input').focus();
                  }
                  autoResize(textarea);
                  toggleLoadingIcon('hide');
              });
          }).catch(error => {
                console.error('Error uploading recording:', error);
                showNotification(error)
                autoResize(textarea);
                toggleLoadingIcon('hide');
          });
      }).catch(error => {
          console.error('Error in recording:', error);
          showNotification(error)
          autoResize(textarea);
          toggleLoadingIcon('hide');
      });

      }
  });

  Mousetrap.bindGlobal('alt+r', function(e) {
      if ($('#record-button').attr('name') === 'record') {
          e.preventDefault();
          $('#record-button').click();
      }
  });
  Mousetrap.bindGlobal('alt+l', function(e) {
      if ($('#lang-toggle-button').attr('name') === 'lang-record') {
          e.preventDefault();
          $('#lang-toggle-button').click();
      }
  });

  $('#message-input').keydown(function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      $('#message-form').submit();
      autoResize(this);
    }
    else if (event.key === 'Enter' && event.shiftKey) {
        event.preventDefault();
        this.value += '\n';
        autoResize(this);
    }
  });

  // Set the initial dark mode state
  setDarkMode(darkMode);

  $('#mode-toggle-button').on('click', function() {
    darkMode = !darkMode;
    setDarkMode(darkMode);
  });
  $('#menu-dark-mode').on('click', function() {
    darkMode = !darkMode;
    setDarkMode(darkMode);
  });

  $.post('/set_language', {'language': languages[currentLanguageIndex]}, function() {});
  $('#lang-toggle-button').on('click', function() {
      var lang_button = $('#lang-toggle-button');

      if (lang_button.hasClass('btn-danger on')) {
          // do nothing
      }
      else if (lang_button.attr('name') === 'pause') {
          pauseAudio();
          lang_button.attr('name', 'unpause');
          lang_button.attr('title', 'Unpause Audio');
          $('#pause-icon').removeClass('fa-pause');
          $('#pause-icon').addClass('fa-play');
      }
      else if (lang_button.attr('name') === 'unpause') {
          playAudio();
          lang_button.attr('name', 'pause');
          lang_button.attr('title', 'Pause Audio');
          $('#pause-icon').removeClass('fa-play');
          $('#pause-icon').addClass('fa-pause');
      }
      else {
          currentLanguageIndex = (currentLanguageIndex + 1) % languages.length;
          $('#lang-text').text(languages[currentLanguageIndex]);
          $('#menu-lang-text').text(languages[currentLanguageIndex]);
          $.post('/set_language', {'language': languages[currentLanguageIndex]}, function() {});
      }
  });
  $('#menu-language').on('click', function() {
      currentLanguageIndex = (currentLanguageIndex + 1) % languages.length;
      $('#lang-text').text(languages[currentLanguageIndex]);
      $('#menu-lang-text').text(languages[currentLanguageIndex]);
      $.post('/set_language', {'language': languages[currentLanguageIndex]}, function() {});
  });

  $('#save-session').on('click', function() {
    $.get("/save_session", function(response) {
        if (response['success']) {
            var saveButton = $('#save-session');
            var saveIcon = $('#save-icon');

            saveButton.addClass('btn-green');
            saveIcon.removeClass('fa-floppy-disk');
            saveIcon.addClass('fa-check');
            saveIcon.addClass('fa-bounce');

            setTimeout(function () {
                saveButton.removeClass('btn-green');
                saveIcon.removeClass('fa-check');
                saveIcon.removeClass('fa-bounce');
                saveIcon.addClass('fa-floppy-disk');
            }, 2000); // 2000 ms = 2 seconds
        }
    });
  });
  $('#menu-save-session').on('click', function() {
    $.get("/save_session", function(response) {
        if (response['success']) {
            var saveIcon = $('#menu-save-icon');

            saveIcon.removeClass('fa-floppy-disk');
            saveIcon.addClass('fa-check');
            saveIcon.addClass('fa-bounce');

            setTimeout(function () {
                saveIcon.removeClass('fa-check');
                saveIcon.removeClass('fa-bounce');
                saveIcon.addClass('fa-floppy-disk');
                menuToggle();
            }, 1000); // 2000 ms = 2 seconds
        }
    });
  });

  $('#load-saved-session').on('click', function() {
    $.get("/load_session", function(response) {
        var messages = response['messages'];
        if (messages.length > 0) {
            var loadIcon = $('#load-saved-icon');
            loadIcon.addClass("fa-spin");
            loadPastMessages(messages);
            setTimeout(function () {
                loadIcon.removeClass("fa-spin")
            }, 2000);
        } else {
            var loadButton = $('#load-saved-session');
            var loadIcon = $('#load-saved-icon');

            loadButton.addClass('btn-danger on');
            loadIcon.removeClass('fa-rotate-right');
            loadIcon.addClass('fa-comment-slash');
            loadIcon.addClass('fa-shake');

            setTimeout(function () {
                loadButton.removeClass('btn-danger off');
                loadIcon.removeClass('fa-comment-slash');
                loadIcon.removeClass('fa-shake');
                loadIcon.addClass('fa-rotate-right');
            }, 2000); // 2000 ms = 2 seconds
        }
    });
  });
  $('#menu-load-session').on('click', function() {
    var loadIcon = $('#menu-load-icon');
    loadIcon.addClass("fa-spin");
    $.get("/load_session", function(response) {
        var messages = response['messages'];
        if (messages.length > 0) {
            loadPastMessages(messages);
            setTimeout(function () {
                loadIcon.removeClass("fa-spin")
                menuToggle();
            }, 1000);
        } else {
            loadIcon.removeClass("fa-spin");
            loadIcon.removeClass('fa-rotate-right');
            loadIcon.addClass('fa-comment-slash');
            loadIcon.addClass('fa-shake');

            setTimeout(function () {
                loadIcon.removeClass('fa-comment-slash');
                loadIcon.removeClass('fa-shake');
                loadIcon.addClass('fa-rotate-right');
            }, 2000); // 2000 ms = 2 seconds
        }
    });
  });
});

var message_counter = 1;
function addMessage(sender, message, has_user_recording, is_language_learning, do_not_store) {
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
      button_container.append(record_button);
        record_button.on('click', function() {
            stopPlaying = false;
            $.post('/play_user_recording', {'message_id': message_body.id}, function (response) {});
      });
    } else {
      var record_button = null;
    }
  }
  if (sender === 'user') {
    if (is_language_learning) {
        var sound_on_button = $('<div class="d-block"><button class="btn btn-link user-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
        var translate_button = null;
        button_container.append(sound_on_button);
    } else {
        var sound_on_button = null;
        var translate_button = $('<div class="d-block"><button class="btn btn-link user-button translate-button"><i class="fa fa-language"></i></button></div>');
        button_container.append(translate_button);
    }
  } else {
    var translate_button = $('<div class="d-block"><button class="btn btn-link bot-button translate-button"><i class="fa fa-language"></i></button></div>');
    var sound_on_button = $('<div class="d-block"><button class="btn btn-link bot-button sound-on-button"><i class="fas fa-volume-up"></i></button></div>');
    button_container.append(translate_button);
    button_container.append(sound_on_button);
  }
  message_card.append(button_container);

  message_col.append(img).append(message_card);
  message_row.append(message_col);
  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  var translated_message = false;
  if (translate_button !== null) {
      translate_button.on('click', function() {
        if (!translated_message) {
            $.post('/translate_text', {'text': message_body.html(), 'sender': sender}, function (response) {
                var translated_text = response['message'].replace(/\n/g, "<br>");;
                var original_text = message_body.html();
                var combined_text = original_text + '<hr><em>' + translated_text + '</em>';
                translated_message = true;
                message_body.html(combined_text);
            });
        }
      });
    }
  if (sound_on_button !== null) {
    sound_on_button.on('click', function() {
      stopPlaying = false;
      $.post('/play_bot_recording', {'message_id': message_body.id, 'text': message_body.text(), 'play_existing': 1}, function (response) {});
  });
  }

  message_box.append(message_row);
  message_box.scrollTop(message_box.prop('scrollHeight'));

  if (sender === 'user' && !do_not_store) {
    $.post('/store_message', {'sender': sender, 'message': message}, function (response) {});
  }
}

function toggleLoadingIcon(action) {
    if (action === 'show') {
      $('#logo-image').attr('src', '/static/logo-loading.gif');
    } else if (action === 'hide') {
      $('#logo-image').attr('src', '/static/logo.png');
    }
}


function getResponse(is_initial_message) {
  toggleLoadingIcon('show');
  stopPlaying = false;
  $.post('/get_response', {'is_initial_message': is_initial_message}, function(response) {
      var bot_message = response['message'];
      var message_index = response['message_index'];
      var error_message = response['error'];
      if (error_message !== null) {
          showNotification(error_message);
      }
      addMessage('assistant', bot_message, false);
      getNextMessage(message_index);
  });
}


function getNextMessage(message_index) {
    $.post('/get_next_message', {'message_index': message_index}, function(response) {
        var bot_message = response['message'];
        if (bot_message === null) {
            // No more messages to show
            toggleLoadingIcon('hide');
            return;
        }
        bot_message = bot_message.replace(/\n/g, "<br>");
        updateLastMessage(bot_message);
        getNextMessage(message_index)
    });
}


function updateLastMessage(newContent) {
  var message_box = $('#message-box');
  var last_message_row = message_box.find('.row:last');
  var last_message_card_body = last_message_row.find('.card-body');
  last_message_card_body.html(newContent);
}


function setDarkMode(isDarkMode) {
    if (isDarkMode) {
      $('body').addClass('dark-mode');
      $('#mode-icon').removeClass('fa-sun').addClass('fa-moon');
      $('#menu-mode-icon').removeClass('fa-sun').addClass('fa-moon');
    } else {
      $('body').removeClass('dark-mode');
      $('#mode-icon').removeClass('fa-moon').addClass('fa-sun');
      $('#menu-mode-icon').removeClass('fa-moon').addClass('fa-sun');
    }
}


function loadPastMessages(messages) {
    toggleLoadingIcon('show');
    var message_box = $('#message-box');
    message_box.html("");
    for (var i = 0; i < messages.length; i++) {
      var msg = messages[i];
      addMessage(msg.role, msg.content, false, msg.is_language_learning, true);
    }
    toggleLoadingIcon('hide');
}

function autoResize(textarea) {
  textarea.style.height = '1.5em';
  textarea.style.height = textarea.scrollHeight + 'px';
}

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function menuToggle() {
  var x = document.getElementById("topnav");
  if (x.className === "topnav") {
    x.className += " responsive";
  } else {
    x.className = "topnav";
  }
}

function initChat() {
    initAudio();
    $('#audio-init').hide();
    $('#main-chat').show();
    getResponse(1);
}