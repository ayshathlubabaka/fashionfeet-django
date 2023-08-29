$(document).ready(function() {
    $('#product-name').on('input', function() {
        var keyword = $(this).val();
        if (keyword.length >= 1) {
            $.ajax({
                url: '/autocomplete/', // Replace with the URL for your autocomplete endpoint
                data: { 'keyword': keyword },
                dataType: 'json',
                success: function(data) {
                    var results = '';
                    for (var i = 0; i < data.length; i++) {
                        results += '<div class="autocomplete-result">' + data[i] + '</div>';
                    }
                    $('#autocomplete-results').html(results);
                }
            });
        } else {
            $('#autocomplete-results').html('');
        }
    });

    // Handle click on autocomplete suggestion
    $(document).on('click', '.autocomplete-result', function() {
        var suggestion = $(this).text();
        $('#product-name').val(suggestion);
        $('#autocomplete-results').html('');
    });
});