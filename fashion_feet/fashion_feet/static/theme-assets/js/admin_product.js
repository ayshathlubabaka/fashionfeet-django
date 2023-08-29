// Get the input element for image upload
const imageInput = document.getElementById('images');
  
// Create a new Cropper instance
let cropper;

// Handle image selection
imageInput.addEventListener('change', function(event) {
  const file = event.target.files[0];

  // Read the selected image file
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = document.getElementById('croppedImage');
    img.src = e.target.result;

    // Initialize the Cropper instance
    cropper = new Cropper(img, {
      aspectRatio: 1, // Set the aspect ratio for cropping
      viewMode: 1, // Show the cropped area within the container
    });
  };
  reader.readAsDataURL(file);
});

// Handle form submission
const form = document.getElementById('yourFormId');
form.addEventListener('submit', function(event) {
  event.preventDefault();

  // Get the cropped image data
  const canvas = cropper.getCroppedCanvas();
  const croppedImageData = canvas.toDataURL();

  // Create a hidden input field to hold the cropped image data
  const hiddenInput = document.createElement('input');
  hiddenInput.type = 'hidden';
  hiddenInput.name = 'cropped_image';
  hiddenInput.value = croppedImageData;
  form.appendChild(hiddenInput);

  // Submit the form
  form.submit();
});