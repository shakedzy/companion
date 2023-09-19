$.getScript("/static/common.js");
$.getScript("/static/audio.js");

$(document).ready(function(){
    for (const input_code_and_lang of input_languages_codes_and_names) {  // [iso-6391, language_name]
        $('#user-lang-dropdown').append(new Option(input_code_and_lang[1], input_code_and_lang[0]));
    }
    for (const output_locale_and_lang of output_languages_locales_and_names) {  // [language_locale, language_name]
        $('#tutor-lang-dropdown').append(new Option(output_locale_and_lang[1], output_locale_and_lang[0]));
    }

    $('.image-label').click(function() {
        $('.image-label').removeClass('selected');
        $(this).addClass('selected');
    });
    $('.image-label').first().click();
    $('.form-check-tutor').change(function () {
        setTimeout(update_voices, 0);
    });


    $('#profile-img-url').change(function(){
        var imageUrl = $(this).val();
        var defaultImageUrl = "/static/user.png";
        var profileImage = $('#profile_image');
        profileImage.attr('src', imageUrl);
        profileImage[0].onerror = function() {
            profileImage.attr('src', defaultImageUrl);
        };
    });

    $('#tutor-lang-dropdown').change(function() {
        update_voices();
    });

    $('#listen-to-tutor').click(function () {
        var text = prompt("Enter text:");
        $.post('/play_bot_test_text', {
            'text': text,
            'lang': $('#tutor-lang-dropdown').val(),
            'voice': $('#voices-dropdown').val()
        }, function(response) {
            let file_url = response['file_url'];
            playSingleAudioFile(file_url);
        });
    });

    $('#setup-form').on('submit', function(e) {
        e.preventDefault();  // prevent the form from doing a page refresh
        $.ajax({
            url : $(this).attr('action') || window.location.pathname, // form action url
            type: $(this).attr('method') || 'POST', // form method
            data: $(this).serialize(), // form data
            success: function (data) {
                console.log("Success");
                var button = $('#submit');
                var icon = $('#submit-icon');

                button.addClass('btn-green');
                icon.addClass('fa-bounce');

                setTimeout(function () {
                    button.removeClass('btn-green');
                    icon.removeClass('fa-bounce');
                }, 2000); // 2000 ms = 2
            },
            error: function (jXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    });
});

function update_voices() {
    var gender = "";
    var x = "";
    $('.form-check-tutor:checked').each(function() {
        x = this.id;
        gender = this.id.split("-")[1];
    });
    var language = $('#tutor-lang-dropdown').val();
    console.log(x, gender, language);
    $.post('/get_language_voices', {'language': language, 'gender': gender}, function (response) {
        var voices = response['voices'];
        $('#voices-dropdown').empty();
        for (const voice of voices) {
            $('#voices-dropdown').append(new Option(voice, voice));
        }
    });
}