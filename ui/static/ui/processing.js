/* Processing */

var glevel = 3; // debug level: 0 (production) - 3 (all output)
var autosend = false; // if true, successful recording is always posted, if false depends on debug level (ie only when glevel == 0)
var pcm16_base64 = '';
var TARGET_SAMPLE_RATE = 16000;
var downsample = true;
var demofile = 'https://storage.googleapis.com/pequod/demo.PRT';


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
    if (e == "na") {
        if (glevel > 2) {
            __logdyn("Received no image to display");
        }
        return;
    }

    if (glevel > 2) {
        __logdyn("Received image to be displayed", e);
    }
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
            
            $('#uploaded-file').css({ visibility: 'hidden' });
        });
    }
};

function showLoadingIcon(state){
    var loadingPanel = $('#loading-icon');
    if (state){
        var contentContainer = $('#contentContainer');
        var pos = contentContainer.position();
        var x = pos.left + Math.floor(0.5*(contentContainer.width() - loadingPanel.width()));
        var y = pos.top + 100;
        loadingPanel.css({
            visibility: 'visible',
            top: y,
            left: x
        });
    } else {
        loadingPanel.css({ visibility: 'hidden' });
    }
}

function process_request() {
    if (localStorage.getItem("url_rpt") == "") {
        __response("No file provided, using demo.");
        __logdyn("No file provided, using demo ", demofile);
        localStorage.setItem("url_rpt", demofile);
    }

    __status("Posting request.");
    
    // TODO alert if empty, or don't do anything, make dummy that's only overwritten if available
    var url_rpt = localStorage.getItem("url_rpt");
    
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        //if (this.readyState == 4 && this.status == 202) {
        if (this.readyState == XMLHttpRequest.OPENED) {
            $('.query-view').css({ visibility: 'hidden'} );
            $('.response-view').css({ visibility: 'hidden'} );
            $('.info-view').css({ display: 'none'} );
            $('.list-view').css({ display: 'none'} );
            $('#response-image').css({ display: 'none'} );
            showLoadingIcon(true);
        }
        if (this.readyState == XMLHttpRequest.DONE) {
            __status("Received response.");
            showLoadingIcon(false);
            
            var responseJSON = JSON.parse(this.responseText);
            var display_text = responseJSON["response"];
            __response(display_text);
            $('#response-text').text(display_text);
            $('.response-view').css({ visibility: 'visible'} );
            
            var transcript = responseJSON["transcript"];
            __transcript(transcript);
            $('#query-text').text('"' + transcript + '"');
            $('.query-view').css({ visibility: 'visible'} );
            
            var info_text = responseJSON["info"];
            $('#info-text').text(info_text);
            $('.info-view').css({ display: 'block'} );
            
            var item_text = responseJSON["items"];
            if (item_text != "na") {
                var item_list = item_text.split(';');
                var listItems = $('#list-items');
                listItems.empty();
                for (var item of item_list){
                    var txt = '<li>' + item + '</li>';
                    listItems.append(txt);
                }
                $('.list-view').css({ display: 'block'} );
            }
            
            var image_url = responseJSON["url_image"];
            if (image_url != "na") {
                __image(image_url);
                $('#resultsimg').attr('src', image_url);
                $('#response-image').css({ display: 'block'} );
            }
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
        $('#record-instruction-container').addClass('mic-background');
        startRecording();
    };
    document.body.onkeyup = function (e) {
        stopRecording();
        $('#record-instruction-container').removeClass('mic-background');
    };

    $('#uploaded-file').children('b').text(demofile);
    
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
