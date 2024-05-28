function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  $(document).ready(function() {
      $(".cancel-order-form").submit(function(event) {
          event.preventDefault(); // Prevent the form from submitting normally
          
          if (confirm('Are you sure you want to cancel this order?')) {
              var form = $(this);
              var orderId = form.data("order-id");
              var cancelUrl = form.data("cancel-url");
              
              $.ajax({
                  url: cancelUrl,
                  type: "POST",
                  headers: {
                      "X-CSRFToken": "{{ csrf_token }}"
                  },
                  success: function(data) {
                      if (data.message === "Order cancelled successfully") {
                          var cancelButton = form.find(".cancel-order-btn");
                          cancelButton.text("Cancelled"); // Update the button text
                          cancelButton.prop("disabled", true); // Disable the button
                          cancelButton.css("background-color", "blue");
                          
                          var statusElement = $("#status-" + orderId);
                          statusElement.text("Cancelled"); // Update the status text
                          statusElement.addClass("cancelled-status"); // Apply the "cancelled-status" class
                      }
                  },
                  error: function(error) {
                      console.error(error);
                  }
              });
          }
      });
  });