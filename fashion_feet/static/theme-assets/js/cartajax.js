$(document).ready(function() {
    function updateCartData() {
		
        $.ajax({
            url: '/cart/', 
            method: 'GET',
            success: function(response) {
				console.log('total', response.total)
				console.log('discount', response.discount)
				$('#total').text(response.total);
                $('#delivery-charge').text(response.delivery_charge);
                $('#grand-total').text(response.grand_total);
                $('#discount').text(response.discount);
                
            },
            error: function(error) {
                console.error('An error occurred:', error);
            }
        });
    }

$(document).ready(function() {
    $('.increase-quantity').on('click', function(e) {
        e.preventDefault();
        var form = $(this).closest('.add-to-cart-form');
		var quantityElement = form.closest('.product_data').find('.quantity');
        var subtotalElement = form.closest('.product_data').find('.price');
		
        $.ajax({
            url: form.attr('action'),
            method: form.attr('method'),
            data: form.serialize(),
            success: function(response) {
				
            if ('error' in response) {
				window.alert('Out of Stock: ' + response.error);
            } else {
                var updatedQuantity = response.quantity;
				var updatedSubtotal = response.sub_total;
                quantityElement.text(updatedQuantity);
				subtotalElement.text(updatedSubtotal);
				updateCartData();
				console.log('Updated Quantity:', updatedQuantity);
				console.log('Updated Subtotal:', updatedSubtotal);
            }
		}
        });
    });
});
$(document).ready(function() {
    $('.decrease-quantity').on('click', function(e) {
        e.preventDefault();
        
        var decreaseUrl = $(this).attr('href');
        var cartItemContainer = $(this).closest('.product_data'); // Assuming a container for each cart item
        var quantityElement = cartItemContainer.find('.quantity'); // Update this selector based on your actual structure
        var subtotalElement = cartItemContainer.find('.price'); // Update this selector based on your actual structure
        
        var formData = cartItemContainer.find('.add-to-cart-form').serialize(); // Serialize the form data
        
        $.ajax({
            url: decreaseUrl,
            method: 'GET', // or 'POST' depending on your server implementation
            data: formData,
            success: function(response) {
				console.log(response.quantity)
                var updatedQuantity = response.quantity;
                var updatedSubtotal = response.sub_total;
                if (updatedQuantity < 1){
					cartItemContainer.remove();
				}
				else{
                quantityElement.text(updatedQuantity);
                subtotalElement.text(updatedSubtotal);
				}
				updateCartData();
                console.log('Quantity and Subtotal updated successfully.');
            },
            error: function(error) {
                console.error('An error occurred:', error);
            }
        });
    });
});
$(document).ready(function() {
    $('.remove-btn').on('click', function(e) {
        e.preventDefault();
        
        var removeUrl = $(this).attr('href');
        var cartItemContainer = $(this).closest('.product_data');
        if (confirm('Are you sure you want to delete this item?')){
        $.ajax({
            url: removeUrl,
            method: 'GET', // or 'POST' depending on your server implementation
            success: function(response) {
                // Handle UI update based on the response
                cartItemContainer.remove(); // Remove the cart item container from the DOM
                updateCartData();
                console.log('Cart item removed successfully.');
            },
            error: function(error) {
                console.error('An error occurred:', error);
            }
        });
	}
    });
});
updateCartData();
});