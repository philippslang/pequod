// Recording handler

var pcm16_base64 = '';
var TARGET_SAMPLE_RATE = 16000;
var downsample = true;

// https://github.com/mattdiamond/Recorderjs
// http://watson-developer-cloud.github.io/speech-javascript-sdk/master/speech-to-text_webaudio-l16-stream.js.html
  
var audio_context;
var recorder;
var is_recording = false;


// this is being called on startup and initializes recorder
function startUserMedia(stream) {
	var input = audio_context.createMediaStreamSource(stream);
  if(glevel > 1){
    __log('Media stream created.');
  }
	
	recorder = new Recorder(input);
  
  if(glevel > 1){
    __log('Recorder initialised.');
  }
}


function startRecording() {
  __clearlogdyn();

  if(is_recording == false) {
    recorder && recorder.record();
    is_recording = true;
    
    if(glevel > 2){
      __logdyn('Recording...');
    }
  }
}



function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function stopRecording() {
	recorder && recorder.stop();
  
  
  if(glevel > 2){
    __logdyn('Stopped recording.');
  }
    
	is_recording = false;
  
  // wav conversion in here
  if(glevel > 2){
    showRecording();	
    }
  
  forwardRecording(); 
  
	
	recorder.clear();
}

// float to pcm: http://watson-developer-cloud.github.io/speech-javascript-sdk/master/speech-to-text_webaudio-l16-stream.js.html
function flt32ToPCM16(flts32){
  var output = new DataView(new ArrayBuffer(flts32.length * 2)); // length is in bytes (8-bit), so number samples *2 to get 16-bit length
  for (var i = 0; i < flts32.length; i++) {
    var multiplier = flts32[i] < 0 ? 0x8000 : 0x7fff; // 16-bit signed range is -32768 to 32767
    output.setInt16(i * 2, flts32[i] * multiplier | 0, true); // index, value, little edian
  }
  return output.buffer; // returns the ArrayBuffer
}


// http://stackoverflow.com/questions/27598270/resample-audio-buffer-from-44100-to-16000
// http://watson-developer-cloud.github.io/speech-javascript-sdk/master/speech-to-text_webaudio-l16-stream.js.html
function downsampleToTarget(flts32){
  // downsampling variables
  var filter = [-0.037935, -0.00089024, 0.040173, 0.019989, 0.0047792, -0.058675, -0.056487,
    -0.0040653, 0.14527, 0.26927, 0.33913, 0.26927, 0.14527, -0.0040653, -0.056487,  -0.058675,
    0.0047792, 0.019989, 0.040173, -0.00089024, -0.037935 ];
    
  var samplingRateRatio = audio_context.sampleRate / TARGET_SAMPLE_RATE;  
  
  
  var nOutputSamples = Math.floor((flts32.length - filter.length) / samplingRateRatio) + 1;
  
  if(glevel > 2){
    __logdyn('Raw sample number ', flts32.length);
    __logdyn('Downsample factor of ', samplingRateRatio);
    __logdyn('Downsample to ', nOutputSamples);
  }
  
  var outputBuffer = new Float32Array(nOutputSamples);
  
  for (i = 0; i + filter.length - 1 < flts32.length; i++) {
    offset = Math.round(samplingRateRatio * i);
    var sample = 0;
    for (var j = 0; j < filter.length; ++j) {
      sample += flts32[offset + j] * filter[j];
    }
    outputBuffer[i] = sample;
  }
  
  return outputBuffer;
}


// mono out of stereo by simple mean
function averageStereo(buffers){

  buffer0 = buffers[0];
  buffer1 = buffers[1];
  
  if(glevel > 2){
    __logdyn('Averaging stereo to mono');
  }  
  
  for (i = 0; i < buffer0.length; i++) {
    buffer0[i] = (buffer0[i]+buffer1[i])/2.0;
  }
  
  return buffer0;
}



//  https://github.com/daaain/JSSoundRecorder
function postProcessRecording(){
  recorder && recorder.getBuffer(function(buffers) {
    // for now, we use first channel only
    var buffer = buffers[0];
    
    if(buffers.length == 2){
      buffer = averageStereo(buffers);
    }
    
    if(downsample && buffer.length != 0){
      buffer = downsampleToTarget(buffer);
    }            
    
    // we convert the 4 byte floats to 2 byte pcm
    var pcm16_buffer = flt32ToPCM16(buffer);
    
    // now we need the base64 encoding of the buffer
    pcm16_base64 = base64ArrayBuffer(pcm16_buffer);   
    
    // https://github.com/mattdiamond/Recorderjs
    //var new_buffer = audio_context.createBuffer(2, buffers[0].length, audio_context.sampleRate);
	});
}


// wav export here, don't call in production for performance
function showRecording() {
	recorder && recorder.exportWAV(function(blob) {
		var url = URL.createObjectURL(blob);
		var li = document.createElement('li');
		var au = document.createElement('audio');
		var hf = document.createElement('a');
		
		au.controls = true;
		au.src = url;
		hf.href = url;
		hf.download = new Date().toISOString() + '.wav';
		//hf.innerHTML = hf.download;
		li.appendChild(au);
		li.appendChild(hf);
		
    while(recordingslist.firstChild){
      		recordingslist.removeChild(recordingslist.firstChild);
    }

		recordingslist.appendChild(li);
	});
}


function forwardRecording(){

  postProcessRecording();  
  
  if(glevel > 2){
    __logdyn('PCM 16 base64 encoded size', pcm16_base64.length);
  }
  
  if(glevel == 0 || autosend)
  {
    if(pcm16_base64.length > 0)
    {
      process_request();      
    }
    else{
      __status("Recording empty");
    }
  }
}