$(document).ready(function(){
    var voices_by_features = null;

    for (const input_code_and_lang of input_languages_codes_and_names) {  // [iso-6391, language_name]
        $('#user-lang-dropdown').append(new Option(input_code_and_lang[1], input_code_and_lang[0]));
    }

    $('.image-label').click(function() {
        $('.image-label').removeClass('selected');
        $(this).addClass('selected');
    });
    $('.image-label').first().click();


    $('#image_url').change(function(){
        var imageUrl = $(this).val();
        var defaultImageUrl = "/static/user.png";
        var profileImage = $('#profile_image');
        profileImage.attr('src', imageUrl);
        profileImage[0].onerror = function() {
            profileImage.attr('src', defaultImageUrl);
        };
    });

});