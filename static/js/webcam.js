var video, image, drawing, logarea;
var facerect;

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

  // upload to server
  var response = fetch('/image/detectface', {
    method: 'POST',
    body: formData
  }).then(function(response) {
    return response.json();
  }).then(function(result) {
    log('detected face');
    // draw to canvas
    var drawingContext = drawing.getContext('2d');
    drawingContext.fillStyle = 'rgba(225,225,225,0.5)';
    drawingContext.fillRect(...result.rect);
    // store rect to state
    facerect = result.rect;
  });
};

var maskCallback = function(event) {
  var imageData = image.toDataURL();
  var formData = new FormData();
  formData.append('image', imageData);
  formData.append('rect', facerect);

  log('masking');
  var response = fetch('/image/mask', {
    method: 'POST',
    body: formData
  }).then(function(response) {
    return response.json();
  }).then(function(result) {
    log('got crop');
    // clear existing image and drawing
    clearCanvas(image);
    clearCanvas(drawing);
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
    
    // draw frame
    var drawingContext = drawing.getContext('2d');
    drawingContext.fillStyle = 'rgba(225,225,225,1)';
    drawingContext.fillRect(facerect);
  });
}

var resetCallback = function(event) {
  log('reset');
  clearCanvas(image);
  hideElement(image);

  clearCanvas(drawing);
  hideElement(drawing);

  showElement(video);
}

function main() {
  video = document.getElementById('video');
  image = document.getElementById('image');
  drawing = document.getElementById('drawing');
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