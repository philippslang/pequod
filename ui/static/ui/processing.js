/* Processing */

var glevel = 3; // debug level: 0 (production) - 3 (all output)
var autosend = false; // if true, successful recording is always posted, if false depends on debug level (ie only when glevel == 0)
var pcm16_base64 = '';
var TARGET_SAMPLE_RATE = 16000;
var downsample = true;


function __log(e, data) {
    logpersistent.innerHTML += "\n" + e + " " + (data || '');
}
function __logdyn(e, data) {
    logdynamic.innerHTML += "\n" + e + " " + (data || '');
}
function __clearlogdyn() {
    logdynamic.innerHTML = "";
}
function __transcript(e) {
    document.getElementById("transcript").innerHTML = 'You: \"' + e + '\"';
}
function __response(e) {
    document.getElementById("response").innerHTML = 'IX: \"' + e + '\"';
}
function __status(e) {
    document.getElementById("status").innerHTML = e;
}
function __image(e) {
    var rimg = document.getElementById("resultsimg");

    if (e == "na") {
        document.getElementById('resultsimg').style.visibility = 'hidden';

        if (glevel > 2) {
            rimg.src = "{% static 'ui/placeholder.png' %}";
            __logdyn("Received no image to display");
        }
        return;
    }

    if (glevel > 2) {
        __logdyn("Received image to be displayed", e);
    }

    rimg.src = e;
    rimg.height = 400;
    document.getElementById('resultsimg').style.visibility = 'visible';
}


Dropzone.options.rptdropzone = {
    paramName: "rptfile",
    maxFiles: 1,
    dictDefaultMessage: "Drop PRT file here",
    maxFilesize: 5,
    init: function () {
        this.on("maxfilesexceeded", function (file) {
            this.removeAllFiles();
            this.addFile(file);
        });
        this.on("success", function (file, responseText) {
            // TODO check if good? no, because this only happens on success
            localStorage.setItem("url_rpt", responseText["public_url"]);
            if (glevel > 2) {
                __logdyn("Set file rpt to ", localStorage.getItem("url_rpt"));
            }

            file.previewTemplate.appendChild(document.createTextNode(responseText["public_url"]));
            $('#record-instruction').removeClass('pequod-hidden');
            var loadingIcon = $('#mic-icon');
            loadingIcon.children('img').removeClass('pequod-hidden');
        });
    }
};


function process_request() {
    if (localStorage.getItem("url_rpt") == "") {
        __status("No file has been uploaded.");
        return;
    }

    __status("Posting request.");
    
    // TODO alert if empty, or don't do anything, make dummy that's only overwritten if available
    var url_rpt = localStorage.getItem("url_rpt");
    
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        //if (this.readyState == 4 && this.status == 202) {
        if (this.readyState == XMLHttpRequest.OPENED) {
            $('#loading-icon').removeClass("pequod-hidden");
        }
        if (this.readyState == XMLHttpRequest.DONE) {
            __status("Received response.");

            var responseJSON = JSON.parse(this.responseText);
            var display_text = responseJSON["response"];
            __response(display_text);
            display_text = responseJSON["url_image"];
            __image(display_text);

            if (glevel > 2) {
                display_text = responseJSON["transcript"];
                __transcript(display_text);
            }
            $('#loading-icon').addClass("pequod-hidden");
        }
    };
    xhttp.open("POST", "/inspector/request/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({ url_rpt: url_rpt, base64_audio: pcm16_base64 }));
    
    __status("Waiting for response.");
}

// All init things go in here
function initializeDocument() {
    // empty default file name
    localStorage.setItem("url_rpt", "");

    document.body.onkeydown = function (e) {
        $('#mic-icon').removeClass('pequod-hidden');
        startRecording();
    };
    document.body.onkeyup = function (e) {
        stopRecording();
        $('#mic-icon').addClass('pequod-hidden');
    };

    document.getElementById('resultsimg').style.visibility = 'hidden';

    // enable debug elements
    if (glevel > 0) {


        document.getElementById('gpost').style.visibility = 'visible';

        __log('This is a debug version with high verbosity.');
        __log('Debug level: ', glevel);
        if (autosend) {
            __log('Autosend successful recording enabled');
        }
        else {
            __log('Autosend successful recording disabled');
        }
    } else {
        $('#debugContainer').addClass('pequod-hidden');
    }

    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;

        if (glevel > 1) {
            __log('Audio context set up.');
            __log('JS navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
        }
    } catch (e) {
        alert('No web audio support in this browser!');
    }

    navigator.getUserMedia({ audio: true }, startUserMedia, function (e) {
        if (glevel > 1) {
            __log('No live audio input: ' + e);
        }
    });
}
