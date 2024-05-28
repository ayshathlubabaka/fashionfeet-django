$(document).ready(function() {
    $('.nav-menu li').click(function() {
      $('.nav-menu li').removeClass('active');
      $(this).addClass('active');
    });
  });

  $(document).ready(function() {
      // Get the current value of the sort parameter from the URL
      var currentSort = new URLSearchParams(window.location.search).get('sort');

      // If the sort parameter is available, set it as the dropdown menu label and move it to the top of the dropdown menu
      if (currentSort) {
          var selectedOption = $('a[data-sort="' + currentSort + '"]');
          $('#selectedButton').text(selectedOption.text());
          selectedOption.addClass('selected');
          selectedOption.parent().prependTo(selectedOption.parent().parent());
      }

      // Handle click event on sorting options
      $('.dropdown-item').on('click', function() {
          // Remove the 'selected' class from all sorting options
          $('.dropdown-item').removeClass('selected');

          // Set the clicked sorting option as the dropdown menu label, move it to the top, and highlight it
          $(this).addClass('selected');
          $('#selectedButton').text($(this).text());
          $(this).parent().prependTo($(this).parent().parent());
      });
  });