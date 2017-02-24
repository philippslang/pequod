/* Processing */

var glevel = 0; // debug level: 0 (production) - 3 (all output)
var autosend = false; // if true, successful recording is always posted, if false depends on debug level (ie only when glevel == 0)
var pcm16_base64 = '';
var TARGET_SAMPLE_RATE = 16000;
var downsample = true;
var demofile = 'https://storage.googleapis.com/pequod/demo.PRT';
var fileNameNode = null;

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

function isMSIE() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");
    return (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./));  // If Internet Explorer, return version number
}

Dropzone.options.rptdropzone = {
    paramName: "rptfile",
    maxFiles: 1,
    dictDefaultMessage: "Drop INTERSECT PRT file here",
    maxFilesize: 5,
    init: function () {
        this.on("maxfilesexceeded", function (file) {
            this.removeAllFiles();
            this.addFile(file);
        });
        this.on("sending", function (file, responseText) {
            $('#uploaded-file').remove();
        });
        this.on("success", function (file, responseText) {
            // TODO check if good? no, because this only happens on success
            localStorage.setItem("url_rpt", responseText["public_url"]);
            if (glevel > 2) {
                __logdyn("Set file rpt to ", localStorage.getItem("url_rpt"));
            }

            file.previewTemplate.appendChild(document.createTextNode(responseText["public_url"]));
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
            if (transcript == 'na')
                transcript = '(empty)';
            $('#query-text').text('"' + transcript + '"');
            $('.query-view').css({ visibility: 'visible'} );
            
            var info_text = responseJSON["info"];
            $('#info-text').text(info_text);
            $('.info-view').css({ display: 'block'} );
            
            var item_text = responseJSON["items"];
            if (item_text && item_text != "na") {
                var item_list = item_text.split(';');
                var listItems = $('#list-items');
                listItems.empty();
                for (var i = 0; i < item_list.length; i++){
                    var txt = '<li>' + item_list[i] + '</li>';
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
        $('#microphone-icon').addClass('icon-mc-on');
        startRecording();
    };
    document.body.onkeyup = function (e) {
        stopRecording();
        $('#microphone-icon').removeClass('icon-mc-on');
    };

    var basename = demofile.split('/').reverse()[0];
    
    $('#rptdropzone').append('<div id="uploaded-file" style="margin-top: 60px;">' +
        'No file uploaded. Using default file <a href="' + demofile + '"><b>' +
        basename + '</b></a>.' +
        '<div>');
    
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
        $('#debugContainer').css({ display: 'none' });
    }

    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;
        
        audio_context = new AudioContext();

        if (glevel > 1) {
            __log('Audio context set up.');
            __log('JS navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
            __log('JS navigator.mediaDevices.getUserMedia ' +
                    (navigator.mediaDevices && navigator.mediaDevices.getUserMedia ? 'available.' : 'not present!'));
        }
    } catch (e) {
        document.getElementById('contentContainer').innerHTML =
            '<div style="text-align: left; margin-left: 100px; margin-top: 10px">' +
            'No web audio support in this browser. ' +
            'Google Chrome or Firefox is recommended for The Pequod.' +
            '</div>';
        return;
    }

    if (navigator.getUserMedia){
        navigator.getUserMedia({ audio: true }, startUserMedia, function (e) {
            if (glevel > 1) {
                __log('No live audio input: ' + e);
            }
        });
    } else if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
        navigator.mediaDevices.getUserMedia({ audio: true }).then(startUserMedia).catch(function(e) {
            if (glevel > 1) {
                __log('No live audio input: ' + e);
            }
        });        
    } else if (window.getUserMedia){
        window.getUserMedia({ audio: true, el: 'media-content' }, startUserMedia, function (e) {
            if (glevel > 1) {
                __log('No live audio input: ' + e);
            }
        });       
    }
}
