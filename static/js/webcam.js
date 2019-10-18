var video, image, drawing, loading, logarea;

function log(text) {
  console.log(text);
  logarea.textContent = text+'\n'+logarea.textContent;
}
function hideElement(element) {
  element.classList.remove('d-block');
  element.classList.add('d-none')
}
function showElement(element) {
  element.classList.remove('d-none');
  element.classList.add('d-block');
}
function clearCanvas(canvas) {
  context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
}

var videoCallback = function(stream) {
  log('got video stream');
  video.srcObject = stream;
  video.play();
};

var snapCallback = function(event) {
  log('snap!');
  
  // pause video, draw current frame to canvas
  var imageContext = image.getContext('2d');
  imageContext.drawImage(video, 0, 0, video.width, video.height);
  hideElement(video);
  showElement(image);
  showElement(drawing);

  // convert canvas to base64 image, put in form
  var imageData = image.toDataURL();
  var formData = new FormData();
  formData.append('image', imageData);
  log('uploading');

  // show processing indicator
  showElement(loading);

  var response = fetch('/image/mask', {
    method: 'POST',
    body: formData
  }).then(function(response) {
    if (response.ok) {
     return response.json();
    } else {
      log('error '+response.error);
      return false;
    }
  }).then(function(result) {
    if (!result) { return; }
    log('got mask');
    // clear existing image and drawing
    clearCanvas(image);
    clearCanvas(drawing);
    hideElement(loading);
    console.log(result);

    var imageContext = image.getContext('2d');
    // add background color
    imageContext.fillStyle = "#BDDECF";
    imageContext.fillRect(0, 0, image.width, image.height)

    // draw image to canvas, with reduced opacity
    var maskImage = new Image();
    // weird trick to ensure image element is created before drawing
    maskImage.onload = function() {
      imageContext.globalCompositeOperation = 'luminosity'
      imageContext.drawImage(maskImage, 0, 0, image.width, image.height);
      imageContext.globalCompositeOperation = 'none';
    }
    maskImage.src = result.image; // set src from result dataURI
  });
}

var resetCallback = function(event) {
  log('reset');
  clearCanvas(image);
  hideElement(image);

  clearCanvas(drawing);
  hideElement(drawing);

  hideElement(loading);
  showElement(video);
}

function main() {
  video = document.getElementById('video');
  image = document.getElementById('image');
  drawing = document.getElementById('drawing');
  loading = document.getElementById('loading')
  logarea = document.getElementById('log');

  if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    log('getUserMedia');
    navigator.mediaDevices.getUserMedia({ audio: false, video: true }).then(videoCallback);
  } else {
    alert('Your browser doesn\'t support getUserMedia. Sorry ;_;')
  }

  document.getElementById("snap").addEventListener("click", snapCallback);
  document.getElementById("mask").addEventListener("click", maskCallback);
  document.getElementById("reset").addEventListener("click", resetCallback);
}

window.onload = main;