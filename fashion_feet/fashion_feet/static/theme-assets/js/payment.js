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

			var amount = "{{grand_total}}";
			var url = "{% url 'payments' %}"
			var csrftoken = getCookie('csrftoken');
			var orderID = "{{order.order_number}}"
			var payment_method = "PayPal"
			var redirect_url = "{% url 'order_complete' %}"
			// Render the PayPal button into #paypal-button-container
paypal.Buttons({
     // Set up the transaction
     createOrder: function(data, actions) {

		var inrAmount = amount; // Replace with your actual INR amount
        var exchangeRate = 0.014; // Replace with the actual exchange rate
        var usdAmount = inrAmount * exchangeRate;

          return actions.order.create({
              purchase_units: [{
                   amount: {
                      value: usdAmount.toFixed(2),
                      currency_code: 'USD'
                   }
               }]
           });
         },
       // Finalize the transaction
       onApprove: function(data, actions) {
           return actions.order.capture().then(function(orderData) {
               // Successful capture! For demo purposes:
			   console.log(orderData)
			   sendData();
						function sendData(){
							fetch(url,{
								method : "POST",
								headers : {
									"CONTENT_TYPE" : "application/json",
									"X-CSRFToken" : csrftoken,
								},
								body : JSON.stringify({
									orderID: orderID,
									transID: orderData.id,
									payment_method: payment_method,
									status: orderData.status,
								}),
							})
							.then(response => response.json())
							.then(data => {
								window.location.href = redirect_url + '?order_number='+data.order_number+'&payment_id='+data.transID;
							});
							
						}
            });
         }
}).render('#paypal-button-container');