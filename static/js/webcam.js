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
  var canvasContext = canvas.getContext('2d');
  loadAndDrawImage('/static/guide.svg', canvasContext);
}
function loadAndDrawImage(src, context, x, y) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.addEventListener("load", () => {
      resolve(img);

      context.drawImage(img,0,0,img.width,img.height);
    });
    img.addEventListener("error", err => reject(err));
    img.src = src;
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
  var imageContext = image.getContext('2d');
  loadAndDrawImage('/static/example.png', imageContext).then(function() {
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

    var imageContext = image.getContext('2d');
    // add background color
    imageContext.fillStyle = "#BDDECF";
    imageContext.fillRect(0, 0, image.width, image.height);

    // load resulting data URI into image canvas, as grayscale
    imageContext.globalCompositeOperation = 'luminosity';
    loadAndDrawImage(result.image, imageContext);
    imageContext.globalCompositeOperation = 'none';
  });
}

var resetCallback = function(event) {
  clearCanvas(image);
  hideElement(image);

  clearCanvas(drawing);
  drawGuide(drawing);
  showElement(drawing);

  hideElement(loading);
  showElement(video);

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