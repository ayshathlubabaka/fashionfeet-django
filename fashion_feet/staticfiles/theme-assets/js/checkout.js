function displayCouponCode() {
    // Get the entered coupon code
    var couponCode = document.getElementById("couponInput").value;

    // Display the coupon code below the button
    var displayCoupon = document.getElementById("displayCoupon");
    displayCoupon.textContent = "Entered Coupon Code: " + couponCode;
  }
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


        //   var amount = "{{grand_total}}";
        //   var url = "{% url 'payments' %}"
        //   var csrftoken = getCookie('csrftoken');
        //   var orderID = "{{order.order_number}}"
        //   var payment_method = "PayPal"

        //   paypal.Button.render({
  
        //       env: 'sandbox', // sandbox | production
  
        //       // PayPal Client IDs - replace with your own
        //       // Create a PayPal app: https://developer.paypal.com/developer/applications/create
        //       client: {
        //           sandbox:    'ASseBc-y7Aii5DpiCX-apdmwFslGApdCnYBeavMfxqTnhWMKm-8gtvmNhHyY-k_EjxeQ9aOT6OqP6Ryl',
        //           production: '<insert production client id>'
        //       },
  
        //       // Show the buyer a 'Pay Now' button in the checkout flow
        //       commit: true,
  
        //       // payment() is called when the button is clicked
        //       payment: function(data, actions) {
  

        //           var exchangeRate = 0.012;
        //           var inrAmount = amount;
        //          var usdAmount = inrAmount * exchangeRate;
        //           // Make a call to the REST api to create the payment
        //           return actions.payment.create({
        //               payment: {
        //                   transactions: [
        //                       {
        //                           amount: { total: usdAmount.toFixed(2), currency: 'USD' }
        //                       }
        //                   ]
        //               }
        //           });
        //       },
  
        //       // onAuthorize() is called when the buyer approves the payment
        //       onAuthorize: function(data, actions) {

                  
  
        //           // Make a call to the REST api to execute the payment
        //           return actions.payment.execute().then(function() {

        //               console.log(details)
        //               sendData();
        //               function sendData(){
        //                   fetch(url,{
        //                       method : "POST",
        //                       headers : {
        //                           "Content-type" : "application/json",
        //                           "X-CSRF Token" : csrftoken,
        //                       },
        //                       body : JSON.stringify({
        //                           orderID: orderID,
        //                           transID: details.id,
        //                           payment_method: payment_method,
        //                           status: details.status,
        //                       }),
        //                   })
        //                   .then(response => response.json())
        //                   .then(data => console.log(data));
        //               }
        //           });
        //       }
  
        //   }, '#paypal-button-container');

          document.getElementById("offer-form").addEventListener("submit", function(event) {
              var selectedOffer = document.querySelector('input[name="offer"]:checked');
              if (!selectedOffer) {
                  event.preventDefault();
                  alert("Please select one offer.");
              }
          });