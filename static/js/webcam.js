var video, image, drawing, loading, logarea;

function log(text) {
  console.log(text);
  logarea.textContent = text+'\n'+logarea.textContent;
}
function hideElement(element) {
  element.classList.remove('d-inline');
  element.classList.remove('d-block');
  element.classList.add('d-none')
}
function showElement(element, inline) {
  element.classList.remove('d-none');
  element.classList.add(inline ? 'd-inline':'d-block');
}
function clearCanvas(canvas) {
  context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
}
function drawGuide(canvas) {
  // gives a nice ellipse for the user to place their head in
  var centerX = canvas.width/2;
  var centerY = canvas.height*2/5;
  var radiusX = canvas.height/5;
  var radiusY = canvas.height/4;
  
  var context = canvas.getContext('2d');
  context.strokeStyle = 'white';
  context.lineWidth = 5;
  context.beginPath();
  context.ellipse(centerX, centerY, radiusX, radiusY,
    0, // rotation
    0, 2 * Math.PI); // start, end radians
  context.stroke();
  context.closePath();
}
function loadAndDrawImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.addEventListener("load", () => resolve(img));
    img.addEventListener("error", err => reject(err));
    img.src = src;

    var imageContext = image.getContext('2d');
    imageContext.drawImage(img,0,0,img.width,img.height);
  });
};

var videoCallback = function(stream) {
  log('got video stream');
  video.srcObject = stream;
  video.play();
};

var snapCallback = function(event) {
  log('snap!');
  clearCanvas(image);
  
  // pause video, draw current frame to canvas
  var imageContext = image.getContext('2d');
  imageContext.drawImage(video, 0, 0, video.width, video.height);
  hideElement(video);
  showElement(image);
  showElement(drawing);

  uploadImageFromCanvas();
}

var uploadCallback = function(event) {
  log('file!');
  clearCanvas(image);

  loadAndDrawImage('/static/example.png').then(function() {
    hideElement(video);
    showElement(image);
    showElement(drawing);

    uploadImageFromCanvas();
  });
}

var uploadImageFromCanvas = function() {
  // convert canvas to base64 image, put in form
  var imageData = image.toDataURL();
  var formData = new FormData();
  formData.append('image', imageData);
  log('uploading');

  // show processing indicator
  showElement(loading, true);

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

    // load resulting data URI into image canvas
    loadAndDrawImage(result.image);

    // TODO, filter so it's greyscale?
  });
}

var resetCallback = function(event) {
  clearCanvas(image);
  hideElement(image);

  clearCanvas(drawing);
  showElement(drawing);

  hideElement(loading);
  showElement(video);

  drawGuide(drawing);
  log('reset');
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
  document.getElementById("upload").addEventListener("click", uploadCallback);
  document.getElementById("reset").addEventListener("click", resetCallback);

  resetCallback();
}

window.onload = main;