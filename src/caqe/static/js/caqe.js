/**
 * Represents a group of audio files.
 * @constructor
 * @param {string} ID - The identifier
 */
function AudioGroup (ID) {
    this.ID = ID;
    this.loopAudio = false;
    this.audioPlayingID = -1;
    this.audioSoloingID = -1;
    this.syncIDs = [];

    $('body').append('<div id="' + this.ID + '"></div>');
}


AudioGroup.prototype.onTimeUpdate = function () {
};
AudioGroup.prototype.onLoadedData = function () {
};
AudioGroup.prototype.onError = function (e) {
};
AudioGroup.prototype.onPause = function () {
};

AudioGroup.prototype.onEnded = function () {
    if (this.loopAudio) {
        this.play(this.audioPlayingID);
    } else {

    }
};


AudioGroup.prototype.addAudio = function (path, ID) {
    // create audio element
    var audioelement = document.createElement('audio');

    // set attributes
    audioelement.setAttribute('src', path);
    audioelement.setAttribute('class', 'audioelements');
    audioelement.setAttribute('id', this.ID + '_audio' + ID);
    audioelement.setAttribute('preload', 'auto');
    audioelement.loop = this.loopAudio;

    // add event listeners
    audioelement.addEventListener('timeupdate', this.onTimeUpdate);
    audioelement.addEventListener('loadeddata', this.onLoadedData);
    audioelement.addEventListener('error', this.onError);
    audioelement.addEventListener('ended', this.onEnded);
    audioelement.addEventListener('pause', this.onPause);
    audioelement.load();

    // add audio element to audio group
    $('#' + this.ID).append(audioelement);
};


AudioGroup.prototype.setSyncIDs = function(syncIDs) {
    var audioelement, duration;

    audioelement = $('#' + this.ID + '_audio' + syncIDs[0]).get(0);
    duration = audioelement.duration;

    for (var i=0; i < syncIDs.length; i++) {
        audioelement = $('#' + this.ID + '_audio' + syncIDs[i]).get(0);
        if (duration != audioelement.duration) {
            // require them to be the same duration for now. in the future maybe we can just loop at the longest...
            // right now we just loop on the first I think.
            //alert("Sync'd audio tags must be the same duration.");
            //return
        }
    }

    this.syncIDs = syncIDs;
};


AudioGroup.prototype.clear = function () {
    $('#' + this.ID).find('.audioelements').remove();
};


AudioGroup.prototype.play = function (ID) {
    var audioelement = $('#' + this.ID + '_audio' + ID).get(0);
    audioelement.currentTime = 0;
    audioelement.play();
    this.audioPlayingID = ID;
    this.audioSoloingID = ID;
};


AudioGroup.prototype.playMarker = function (ID, Time) {
    var audioelement = $('#' + this.ID + '_audio' + ID).get(0)
    audioelement.currentTime = Time;
    audioelement.play();
    this.audioPlayingID = ID;
    this.audioSoloingID = ID;
};

AudioGroup.prototype.playSelection = function (ID, StarTime, EndTime) {
    var audioelement = $('#' + this.ID + '_audio' + ID).get(0)
    audioelement.load();
    audioelement.currentTime = StarTime;
    audioelement.play();
    this.audioPlayingID = ID;
    this.audioSoloingID = ID;
    audioelement.ontimeupdate = function(){
        if(audioelement.currentTime >= EndTime){
            audioelement.pause();
        };

        if(audioelement.length == audioelement.currentTime){
            audioelement.currentTime = 0.0;
        };
    };
};


AudioGroup.prototype.pause = function () {
    if (this.audioPlayingID == -2) {
        this.syncPause();
    } else {
        if (this.audioPlayingID !== -1) {
            var audioelement = $('#' + this.ID + '_audio' + this.audioPlayingID).get(0);
            audioelement.pause();
            this.audioPlayingID = -1;
        }
    }

    this.audioSoloingID = -1;
};


AudioGroup.prototype.syncPlay = function() {
    // Play all audio tags in the syncIDs group at once, set audioPlayingID to -2 to indicate sync play
    var audioelement;

    for (var i=0; i < this.syncIDs.length; i++) {
        audioelement = $('#' + this.ID + '_audio' + this.syncIDs[i]).get(0);
        audioelement.currentTime = 0.000001;
        audioelement.play();

        this.audioPlayingID = -2;
    }
};


AudioGroup.prototype.syncPlayMarker = function(Time) {
    // Play all audio tags in the syncIDs group at once, set audioPlayingID to -2 to indicate sync play
    var audioelement;

    for (var i=0; i < this.syncIDs.length; i++) {
        audioelement = $('#' + this.ID + '_audio' + this.syncIDs[i]).get(0);
        audioelement.currentTime = Time;
        audioelement.play();

        this.audioPlayingID = -2;
    }
};

AudioGroup.prototype.syncPause = function() {
    // pause all audio tags in the syncIDs group
    var audioelement;

    if (this.audioPlayingID != -1) {
        for (var i=0; i < this.syncIDs.length; i++) {
            audioelement = $('#' + this.ID + '_audio' + this.syncIDs[i]).get(0);
            audioelement.pause();
        }

        this.audioPlayingID = -1;
    }
};


AudioGroup.prototype.setLoopAudio = function (loop) {
    this.loopAudio = loop;
    $('#' + this.ID + ' > audio').prop('loop', this.loopAudio);
};


AudioGroup.prototype.solo = function (ID) {
    // solo a particular audio element
    var audioelement;
    this.muteAll();

    audioelement = $('#' + this.ID + '_audio' + ID).get(0);
    audioelement.volume = 1;

    this.audioSoloingID = ID;
};


AudioGroup.prototype.muteAll = function () {
    // mute all audio elements
    var audioelement;
    for (var i=0; i < this.syncIDs.length; i++) {
        audioelement = $('#' + this.ID + '_audio' + this.syncIDs[i]).get(0);
        audioelement.volume = 0;

        this.audioSoloingID = -1;
    }
};


/**
 * Manages the evaluation task
 * @constructor
 * @param {string} config - Contains the configuration data for the evaluation task
 */
var EvaluationTaskStateEnum = {
    INTRODUCTION: 0,
    TRAINING: 1,
    EVALUATION: 2,
    SUBMIT: 3,
    COMPLETE: 4
};


function EvaluationTask (config) {
    this.config = config;

    this.audioGroup = new AudioGroup('audioGroup');
    this.audioGroup.setLoopAudio(false);
    this.numAudioElementsLoading = 0;

    this.audioGroup.onTimeUpdate = $.proxy(this.audioOnTimeUpdate, this);
    this.audioGroup.onError = $.proxy(this.audioOnError, this);
    this.audioGroup.onLoadedData = $.proxy(this.audioOnLoadedData, this);
    this.audioGroup.onEnded = $.proxy(this.audioOnEnded, this);
    // this.audioGroup.onPlay = $.proxy(this.audioOnPlay, this);
    this.audioGroup.onPause = $.proxy(this.audioOnPause, this);

    this.stimulusMap = null;
    this.state = EvaluationTaskStateEnum.INTRODUCTION;
    this.currentView = this.views[this.state];
    this.conditionIndex = 0;
    this.completedConditionData = [];

    this.loadTrainingAudio();
    this.loadAllConditionGroupAudio();

    var evaluationTaskHandle = this;
    window.onbeforeunload = function () {
        if (evaluationTaskHandle.state !== EvaluationTaskStateEnum.COMPLETE) {
            return 'The evaluation is not complete. Are you sure you want to leave?';
        }
    }
}


EvaluationTask.prototype.views = [
    '#introduction',
    '#training',
    '#evaluation',
    '#submit',
    '#complete',
    '#error',
    '#loading'];


EvaluationTask.prototype.prependGroupID = function(ID, conditionIndex) {
    if (typeof conditionIndex === 'undefined') { conditionIndex = this.conditionIndex; }

    return 'G' + this.config.conditions[conditionIndex]['groupID'] + '_' + ID;
};


EvaluationTask.prototype.showOnly = function (targetView) {
    for (var i=0; i < this.views.length; i++) {
        if (this.views[i] !== targetView) {
            $(this.views[i]).addClass('hidden');
        }
    }

    $(targetView).removeClass('hidden');
};


EvaluationTask.prototype.audioOnTimeUpdate = function (e) {
    var position;
    if (this.audioGroup.audioPlayingID == -1) {
        $('#playback-position').val(0);
    } else if (this.audioGroup.audioPlayingID == -2) {
        if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioSoloingID)) {
            position = e.target.currentTime / e.target.duration * 100;
            $('#playback-position').val(position);
        }
    } else {
        if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioPlayingID)) {
            position = e.target.currentTime / e.target.duration * 100;
            $('#playback-position').val(position);
        }
    }
};


EvaluationTask.prototype.audioOnError = function (e) {
    $('#error').find('p').html(e.toString());
    this.showOnly('#error');
};


EvaluationTask.prototype.audioOnLoadedData = function () {
    this.numAudioElementsLoading--;

    if (this.numAudioElementsLoading === 0) {
        this.showOnly(this.currentView);
    }
};


EvaluationTask.prototype.audioOnEnded = function () {
    if (this.audioGroup.loopAudio) {
        this.audioGroup.play(this.audioGroup.audioPlayingID);
    } else {
        $('.play-btn').removeClass('disabled disable-clicks btn-success').addClass('btn-default');
        this.audioGroup.audioPlayingID = -1;
    }

    if (this.state===EvaluationTaskStateEnum.TRAINING && this.config.requireListeningToAllTrainingSounds) {
        var qry = $('#training').find('.play-btn').not('.played');
        qry.addClass('disabled disable-clicks');
        if (qry.length != 0) {
            qry.first().removeClass('disabled disable-clicks');
        } else {
            $('#trainingNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');
        }
    }
};

// EvaluationTask.prototype.audioOnPlay = function () {
// }

EvaluationTask.prototype.audioOnPause = function () {
}

EvaluationTask.prototype.loadTrainingAudio = function () {
    var key, value;
    for (key in this.config.referenceExampleDict) {
        if (this.config.referenceExampleDict.hasOwnProperty(key)) {
            value = this.config.referenceExampleDict[key];
            this.addAudio(this.audioGroup, value, 'Training' + key);
        }
    }

    for (key in this.config.qualityExampleDict) {
        if (this.config.qualityExampleDict.hasOwnProperty(key)) {
            value = this.config.qualityExampleDict[key];
            for (var i = 0; i < value.length; i++) {
                this.addAudio(this.audioGroup, value[i], 'Training' + key + i);
            }
        }
    }
};


EvaluationTask.prototype.loadConditionGroupAudio = function (conditionGroupID) {
    var i;
    for (i = 0; i < this.config.conditionGroups[conditionGroupID]['referenceFiles'].length; i++) {
        this.addAudio(this.audioGroup,
            this.config.conditionGroups[conditionGroupID]['referenceFiles'][i][1],
            'G' + conditionGroupID + '_' + this.config.conditionGroups[conditionGroupID]['referenceFiles'][i][0]);
    }
    for (i = 0; i < this.config.conditionGroups[conditionGroupID]['stimulusFiles'].length; i++) {
        this.addAudio(this.audioGroup,
            this.config.conditionGroups[conditionGroupID]['stimulusFiles'][i][1],
            'G' + conditionGroupID + '_' + this.config.conditionGroups[conditionGroupID]['stimulusFiles'][i][0]);
    }
};


EvaluationTask.prototype.loadAllConditionGroupAudio = function () {
    var groupIDs = Object.keys(this.config.conditionGroups);
    for (var i = 0; i < groupIDs.length; i++) {
        this.loadConditionGroupAudio(groupIDs[i]);
    }
};


EvaluationTask.prototype.addAudio = function (group, path, ID) {
    this.numAudioElementsLoading++;
    this.showOnly('#loading');
    group.addAudio(path, ID);
};


EvaluationTask.prototype.startTraining = function () {
    this.state = EvaluationTaskStateEnum.TRAINING;

    if (this.config.requireListeningToAllTrainingSounds) {
        // disable play buttons
        $('#training').find('.play-btn').addClass('disabled disable-clicks').first().removeClass('disabled disable-clicks');

        // disable next button
        $('#trainingNextBtn').addClass('disable-clicks').parent().addClass('disabled');
    }

    this.showOnly('#training');
};


EvaluationTask.prototype.startEvaluation = function () {
    // disable next button
    $('#evaluationNextBtn').addClass('disable-clicks').parent().addClass('disabled');

    // start timer
    this.testTimeout = setTimeout(this.testTimeoutCallback, this.config['testTimeoutSec'] * 1000.0, this);

    this.setTrialCountLabels();

    if (this.config.conditions[this.conditionIndex]['evaluation_instructions_html'] !== 'None') {
        $('#evaluationInstructions').html(this.config.conditions[this.conditionIndex]['evaluation_instructions_html']);
    }
    this.showOnly('#evaluation');
};


EvaluationTask.prototype.testTimeoutCallback = function (_this) {
    $('#evaluationNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');
};


EvaluationTask.prototype.submitResults = function () {
    this.showOnly('#loading');
    this.state = EvaluationTaskStateEnum.SUBMIT;
    var evaluationTaskHandle = this;

    $.ajax({
            type: "POST",
            timeout: 20000,
            url: SUBMISSION_URL,
            data: {'participant_id': PARTICIPANT_ID,
                'completedConditionData':JSON.stringify(this.completedConditionData),
                'config': JSON.stringify(this.config)},
            dataType: 'json'})
        .done( function (response){
            if (response.error==false) {
                evaluationTaskHandle.state = EvaluationTaskStateEnum.COMPLETE;
                window.location.href = TEST_COMPLETE_REDIRECT_URL;
            } else {
                evaluationTaskHandle.showOnly('#submission-error');
            }
        })
        .fail (function (xhr, ajaxOptions, thrownError){
            $('#submission-error').find('p').html(thrownError.toString());
            evaluationTaskHandle.showOnly('#submission-error');
        });
};


EvaluationTask.prototype.playAudio = function(ID) {
    this.audioGroup.play(ID);
    $('.play-btn').removeClass('btn-success').addClass('btn-default disabled disable-clicks');
    $('#play' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played');
};


EvaluationTask.prototype.playReference = function(ID) {
    this.audioGroup.play(this.prependGroupID(ID));
    $('.play-btn').removeClass('btn-success').addClass('btn-default disabled disable-clicks');
    $('#playReference' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played');
};


EvaluationTask.prototype.playStimulus = function(idx) {
    this.audioGroup.play(this.stimulusMap[idx]);
    $('.play-btn').removeClass('btn-success').addClass('btn-default disabled disable-clicks');
    $('#playStimulus' + idx + 'Btn').removeClass('btn-default').addClass('btn-success played');
};


EvaluationTask.prototype.setTrialCountLabels = function () {
    $('#currentTrialLbl').html(this.conditionIndex + 1);
    $('#totalTrialLbl').html(this.config.conditions.length);
};


EvaluationTask.prototype.nextTrial = function () {
    this.saveRatings();
    $('.play-btn').removeClass('played');

    // reset playback position
    $('#playback-position').val(0);

    this.conditionIndex++;
    if (this.conditionIndex >= this.config.conditions.length) {
        this.submitResults();
        return false;
    }

    this.setTrialCountLabels();

    if (this.config.conditions[this.conditionIndex]['evaluation_instructions_html'] !== 'None') {
        $('#evaluationInstructions').html(this.config.conditions[this.conditionIndex]['evaluation_instructions_html']);
    }

    return true;
};


EvaluationTask.prototype.createStimulusMap = function(conditionIndex) {
    alert('Function createStimulusMap() has not been implemented in your inherited class!');
};


EvaluationTask.prototype.saveRatings = function() {
    alert('Function saveRatings() has not been implemented in your inherited class!');
};


/**
 * Inherits from EvaluationTask and manages the MUSHRA task
 * @constructor
 * @param {string} config - Contains the configuration data for the MUSHRA task
 */
MushraTask.prototype = Object.create(EvaluationTask.prototype);
MushraTask.prototype.constructor = MushraTask;

function MushraTask(config) {
    EvaluationTask.apply(this, arguments);
    this.createStimulusMap(this.conditionIndex);
    this.connectSliders();
}

MushraTask.prototype.createStimulusMap = function (conditionIndex) {
    this.stimulusMap = [];
    var i;
    for (i = 0; i < this.config.conditions[conditionIndex]['stimulusKeys'].length; i++) {
        this.stimulusMap[i] = this.prependGroupID(this.config.conditions[conditionIndex]['stimulusKeys'][i],
            conditionIndex);
    }
};


// connect the sliders to the text boxes
MushraTask.prototype.connectSliders = function() {
    $('.mushra-slider').each( function() {
        this.oninput = function() {
            $('#' + this.id + 'Value').get(0).value = this.value;
        };
    });
};

MushraTask.prototype.setSliders = function(value) {
    $('.mushra-slider').each( function() {
        this.value = value;
    });
};


MushraTask.prototype.nextTrial = function () {
    if (EvaluationTask.prototype.nextTrial.apply(this)) {
        this.createStimulusMap(this.conditionIndex);
        this.setSliders(this.config.defaultRatingValue);
    }
};


// save the ratings for the current condition
MushraTask.prototype.saveRatings = function() {
    var conditionRatings = {};
    var stimulusMap = this.stimulusMap;
    $('.mushra-slider').each( function(idx) {
        var re = /G([0-9]+)_([a-zA-Z0-9]+)/;
        var stimulusID = re.exec(stimulusMap[idx])[2];
        conditionRatings[stimulusID] = this.value;
    });

    this.completedConditionData[this.conditionIndex] = {'ratings': conditionRatings,
        'conditionID': this.config.conditions[this.conditionIndex].conditionID,
        'groupID': this.config.conditions[this.conditionIndex].groupID,
        'referenceFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['referenceFiles'],
        'stimulusFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['stimulusFiles'],
        'referenceKeys': this.config.conditions[this.conditionIndex].referenceKeys,
        'stimulusKeys': this.config.conditions[this.conditionIndex].stimulusKeys};
};


/**
 * Inherits from EvaluationTask and manages the pairwise task
 * @constructor
 * @param {string} config - Contains the configuration data for the pairwise task
 */
PairwiseTask.prototype = Object.create(EvaluationTask.prototype);
PairwiseTask.prototype.constructor = PairwiseTask;

function PairwiseTask(config) {
    EvaluationTask.apply(this, arguments);
    this.timeoutPassed = false;
    this.createStimulusMap(this.conditionIndex);
}

PairwiseTask.prototype.startEvaluation = function () {
    EvaluationTask.prototype.startEvaluation.apply(this);

    this.audioGroup.setLoopAudio(true);
};


PairwiseTask.prototype.testTimeoutCallback = function (_this) {
    _this.timeoutPassed = true;
    _this.testNextTrialRequirements();
};


PairwiseTask.prototype.playReference = function(ID) {
    this.audioGroup.solo(this.prependGroupID(ID));
    if (this.audioGroup.audioPlayingID == -1) {
        this.audioGroup.syncPlay();
    }

    $('.play-btn').removeClass('btn-success').addClass('btn-default');
    $('#playReference' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played');

    this.testNextTrialRequirements();
};


PairwiseTask.prototype.playStimulus = function(ID) {
    $('.play-btn').removeClass('btn-success').addClass('btn-default');

    $('.pairwiseStimulusLabel').html('&nbsp;');
    $('.pairwise-stimulus-play-btn').removeClass('pairwise-selected');

    this.audioGroup.solo(this.stimulusMap[ID]);
    if (this.audioGroup.audioPlayingID == -1) {
        this.audioGroup.syncPlay();
    }

    $('#playStimulus' + ID + 'BtnLabel').html('(selected)');
    $('#playStimulus' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played pairwise-selected');

    this.testNextTrialRequirements();
};


PairwiseTask.prototype.stopAllAudio = function() {
    this.audioGroup.syncPause();
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
};


PairwiseTask.prototype.nextTrial = function () {
    this.stopAllAudio();
    if (!this.saveRatings()) {
        return;
    }

    $('.pairwise-stimulus-play-btn').removeClass('pairwise-selected played');
    $('.pairwiseStimulusLabel').html('&nbsp;');

    // disable next button
    $('#evaluationNextBtn').addClass('disable-clicks').parent().addClass('disabled');

    clearTimeout(this.testTimeout);

    // reset playback position
    $('#playback-position').val(0);

    this.conditionIndex++;

    if (this.conditionIndex >= this.config.conditions.length) {
        this.submitResults();
    } else {
        this.createStimulusMap(this.conditionIndex);
        this.setTrialCountLabels();
        if (this.config.conditions[this.conditionIndex]['evaluation_instructions_html'] !== 'None') {
            $('#evaluationInstructions').html(this.config.conditions[this.conditionIndex]['evaluation_instructions_html']);
        }
        this.timeoutPassed = false;
        this.testTimeout = setTimeout(this.testTimeoutCallback, this.config['testTimeoutSec'] * 1000.0, this);
    }
};


PairwiseTask.prototype.testNextTrialRequirements = function () {
    var qry = $('#evaluation');
    var all_played = qry.find('.play-btn').length == qry.find('.play-btn').filter('.played').length;
    var stimulus_selected = $('.pairwise-stimulus-play-btn').hasClass('pairwise-selected');

    if (all_played && stimulus_selected && this.timeoutPassed) {
        $('#evaluationNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');
    }
};


PairwiseTask.prototype.createStimulusMap = function (conditionIndex) {
    var i;
    this.stimulusMap = []
    for (i = 0; i < this.config.conditions[conditionIndex]['stimulusKeys'].length; i++) {
        this.stimulusMap[i] = this.prependGroupID(this.config.conditions[conditionIndex]['stimulusKeys'][i],
            conditionIndex);
    }
    var referenceKeys = [];
    for (i = 0; i < this.config.conditions[conditionIndex]['referenceKeys'].length; i++) {
        referenceKeys.push(this.prependGroupID(this.config.conditions[conditionIndex]['referenceKeys'][i],
            conditionIndex));
    }

    this.audioGroup.setSyncIDs(this.stimulusMap.concat(referenceKeys));
};


// save the ratings for the current condition
PairwiseTask.prototype.saveRatings = function() {
    // make sure something was selected
    if (!$('.pairwise-stimulus-play-btn').hasClass('pairwise-selected')) {
        alert('Press the A or B button to select your preferred recording before continuing.');
        return false;
    }

    var stimulusMap = [];

    var i;
    var re = /G([0-9]+)_([a-zA-Z0-9]+)/;
    for (i = 0; i < this.stimulusMap.length; i++) {
        stimulusMap[i] = re.exec(this.stimulusMap[i])[2];
    }

    // save the selected one
    var conditionRatings = {};
    conditionRatings[stimulusMap[0]] = $('#playStimulus0Btn').hasClass('pairwise-selected') ? 1 : 0;
    conditionRatings[stimulusMap[1]] = $('#playStimulus1Btn').hasClass('pairwise-selected') ? 1 : 0;

    // save the condition data
    this.completedConditionData[this.conditionIndex] = {'ratings': conditionRatings,
        'conditionID': this.config.conditions[this.conditionIndex].conditionID,
        'groupID': this.config.conditions[this.conditionIndex].groupID,
        'referenceFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['referenceFiles'],
        'stimulusFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['stimulusFiles'],
        'referenceKeys': this.config.conditions[this.conditionIndex].referenceKeys,
        'stimulusKeys': this.config.conditions[this.conditionIndex].stimulusKeys};

    return true;

};

/**
 * Inherits from EvaluationTask and manages the segmentation timestamp marking task
 * @constructor
 * @param {string} config - Contains the configuration data for the segmentation timestamp marking task
 */

Segmentation.prototype = Object.create(EvaluationTask.prototype);
Segmentation.prototype.constructor = Segmentation;

function Segmentation(config) {
    EvaluationTask.apply(this, arguments);

    // this.audioPlaying = false;
    // this.audioPaused = true;
    this.audioUpdate = null;
    this.increment = 0.005;

    this.timeoutPassed = false;
    this.createStimulusMap(this.conditionIndex);

    this.stimulusPlayed = false;
    this.segmentVal = null;
}

Segmentation.prototype.startEvaluation = function () {
    // disable next trial button
    $('#evaluationNextBtn').addClass('disable-clicks').parent().addClass('disabled');

    // disable experiment UI before one full listening
    $('#playStimulus0Marker').prop('disabled', true);
    // $('#stopBtn').addClass('disable-clicks').addClass('disabled');
    $('#segmentation-submitBtn').addClass('disable-clicks').addClass('disabled');
    $('#segmentation-nullBtn').addClass('disable-clicks').addClass('disabled');
    $('#segmentation-audio-progress').prop('disabled', true);

    $('#segmentation-marker').css('background-color', 'rgba(188, 246, 227, 1.0)');
    // $('#segmentation-marker').off('click');
    var canvas = $('#segmentation-marker').get(0);
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    $('#segmentation-marker').on('click', function (e){

        var boxOffset = $(this).offset().left;
        var x = (e.pageX - boxOffset)/this.offsetWidth;
        var canvas = $(this).get(0)
        var ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var iStrokeWidth = 1;
        var iTranslate = (iStrokeWidth % 2) / 2;
        ctx.translate(iTranslate, iTranslate);
        ctx.lineWidth = iStrokeWidth;
        ctx.beginPath();

        if(x>0.1){
            var left = x-0.1;
            if(x<0.9){
                var w = 0.2;
            }else{
                var w = 0.1+(1.0-x);
            }
        }else{
            var left = 0.0;
            var w = x +0.1
        }
        ctx.rect(left*canvas.width, 0, w*canvas.width, canvas.height);
        ctx.fillStyle = "#30E3A8";
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(Math.round(x*canvas.width), 0);
        ctx.lineTo(Math.round(x*canvas.width), canvas.height);
        ctx.strokeStyle="Black";
        ctx.stroke();

        ctx.translate(-iTranslate, -iTranslate);
        this.value = x;
    });

    this.setTrialCountLabels();

    if (this.config.conditions[this.conditionIndex]['evaluation_instructions_html'] !== 'None') {
        $('#evaluationInstructions').html(this.config.conditions[this.conditionIndex]['evaluation_instructions_html']);
    }

    this.audioGroup.setLoopAudio(false);
    this.showOnly('#evaluation');
};


Segmentation.prototype.testTimeoutCallback = function (_this) {
    _this.timeoutPassed = true;
    _this.firstFullListen();
    _this.stimulusPlayed = true;
    // _this.testNextTrialRequirements();
};


Segmentation.prototype.playStimulus = function(ID) {
    $('.play-btn').removeClass('btn-success').addClass('btn-default');

    var audioLength = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0).duration;
    var markerValue = $('#segmentation-audio-progress').val();

    this.audioGroup.playMarker(this.stimulusMap[ID], markerValue*audioLength);

    if (!this.stimulusPlayed){
        var audioLength = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0).duration;
        this.testTimeout = setTimeout(this.testTimeoutCallback, audioLength * 1000.0, this);
    }
};


Segmentation.prototype.startTraining = function(){

    this.state = EvaluationTaskStateEnum.TRAINING;

    var trainVideo = $('#tutorial_video').get(0);
    trainVideo.addEventListener('ended', this.videoOnEnded);

    if (this.config.requireListeningToAllTrainingSounds) {
        // disable play buttons
        // $('#training').find('.play-btn').addClass('disabled disable-clicks').first().removeClass('disabled disable-clicks');

        // disable next button
        $('#trainingNextBtn').addClass('disable-clicks').parent().addClass('disabled');
    }

    this.showOnly('#training');
};

Segmentation.prototype.videoOnEnded = function() {

    $('.play-btn').removeClass('disabled disable-clicks btn-success').addClass('btn-default');
    $('#trainingNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');
};


Segmentation.prototype.playTrainingVideo = function(){
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
    var video = $('#tutorial_video').get(0);
    video.play();
};

Segmentation.prototype.playPauseTrainingVideo = function(){
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
    var video = $('#tutorial_video').get(0);

    if(video.paused){
        video.play();
    }else {
        video.pause();
    }

};

Segmentation.prototype.rewindTrainingVideo = function(){
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
    var video = $('#tutorial_video').get(0);
    if(video.currentTime <= 3.0){
        video.currentTime=0.0;
    }else{
        video.currentTime=video.currentTime-3.0;
    };
};


Segmentation.prototype.playStimulusMarker = function(ID) {
    $('.play-btn').removeClass('btn-success').addClass('btn-default');

    var audioLength = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0).duration;
    var markerValue = $('#segmentation-marker').get(0).value;

    this.audioGroup.playMarker(this.stimulusMap[ID], markerValue*audioLength);

}

Segmentation.prototype.playSelection = function(ID) {
    clearInterval(this.audioUpdate);
    $('.play-btn').removeClass('btn-success').addClass('btn-default');

    var audio = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0)
    var audioLength = audio.duration;
    var markerValue = $('#segmentation-marker').get(0).value;

    this.increment = 0.1/ audioLength;

    if(markerValue>0.1){
        var startTime = markerValue-0.1;
    }else{
        var startTime = 0.0;
    }

    if(markerValue<0.9){
        var endTime = markerValue+0.1;
    }else{
        var endTime = 1.0;
    }
    $('#segmentation-audio-progress').val(startTime);
    this.audioGroup.playSelection(this.stimulusMap[ID], startTime*audioLength, endTime*audioLength);
    this.audioUpdate = setInterval(this.audioProgressUpdate, 250, audio);

}


Segmentation.prototype.playPauseStimulus = function(ID){
    clearInterval(this.audioUpdate);

    var audio = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0);
    var audioLength = audio.duration;
    var markerValue = $('#segmentation-audio-progress').val();
    this.increment = 0.25/ audioLength;

    if (!this.stimulusPlayed){

        $('#playStimulusBtn').addClass('disable-clicks').addClass('disabled');
        $('#playStimulusBtn').prop('disabled', true);

        this.audioGroup.playSelection(this.stimulusMap[ID], 0, audioLength);
        this.audioUpdate = setInterval(this.audioProgressUpdate, 250, audio);
        this.testTimeout = setTimeout(this.testTimeoutCallback, audioLength * 1000.0, this);
    }else{

        if(audio.paused){
            // $('.play-btn').removeClass('btn-success').addClass('btn-default');

            this.audioGroup.playSelection(this.stimulusMap[ID], markerValue*audioLength, audioLength);
            this.audioUpdate = setInterval(this.audioProgressUpdate, 250, audio);

        }else {
            this.audioGroup.syncPause();
            clearInterval(this.audioUpdate);
            // $('.play-btn').removeClass('btn-success').addClass('btn-default');
        }
    }
}

Segmentation.prototype.stopAllAudio = function() {
    this.audioGroup.syncPause();
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
};


Segmentation.prototype.submitSliderPosition = function(){
    this.segmentVal = $('#segmentation-marker').get(0).value;
}

Segmentation.prototype.noChangeHeard = function() {
    this.segmentVal = -1;

    var canvas = $('#segmentation-marker').get(0);
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}


Segmentation.prototype.nextTrial = function () {
    this.stopAllAudio();
    if (!this.saveRatings()) {
        return;
    }

    // disable next button
    $('#evaluationNextBtn').addClass('disable-clicks').parent().addClass('disabled');

    $('#segmentation-submitBtn').addClass('disable-clicks').addClass('disabled');
    $('#segmentation-nullBtn').addClass('disable-clicks').addClass('disabled');
    $('#segmentation-audio-progress').prop('disabled', true);

    $('#playStimulus0Marker').prop('disabled', true);

    clearTimeout(this.testTimeout);

    // reset playback position
    // $('#segmentation-marker').off('click');

    var canvas = $('#segmentation-marker').get(0);
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

   $('#segmentation-marker').on('click', function (e){

        var boxOffset = $(this).offset().left;
        var x = (e.pageX - boxOffset)/this.offsetWidth;
        var canvas = $(this).get(0)
        var ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var iStrokeWidth = 1;
        var iTranslate = (iStrokeWidth % 2) / 2;
        ctx.translate(iTranslate, iTranslate);
        ctx.lineWidth = iStrokeWidth;
        ctx.beginPath();

        if(x>0.1){
            var left = x-0.1;
            if(x<0.9){
                var w = 0.2;
            }else{
                var w = 0.1+(1.0-x);
            }
        }else{
            var left = 0.0;
            var w = x +0.1
        }
        ctx.rect(left*canvas.width, 0, w*canvas.width, canvas.height);
        ctx.fillStyle = "#30E3A8";
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(Math.round(x*canvas.width), 0);
        ctx.lineTo(Math.round(x*canvas.width), canvas.height);
        ctx.strokeStyle="Black";
        ctx.stroke();

        ctx.translate(-iTranslate, -iTranslate);
        this.value = x;
    });


    $('#segmentation-audio-progress').val(0);
    this.conditionIndex++;

    if (this.conditionIndex >= this.config.conditions.length) {
        this.submitResults();
    } else {
        this.createStimulusMap(this.conditionIndex);
        this.setTrialCountLabels();
        if (this.config.conditions[this.conditionIndex]['evaluation_instructions_html'] !== 'None') {
            $('#evaluationInstructions').html(this.config.conditions[this.conditionIndex]['evaluation_instructions_html']);
        }
        this.stimulusPlayed = false;
        this.timeoutPassed = false;
        this.segmentVal = null;
        // var audio = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0);
        // this.testTimeout = setTimeout(this.testTimeoutCallback, this.config['testTimeoutSec'] * 1000.0, this);
    }
};


Segmentation.prototype.firstFullListen = function () {
    $('#playStimulus0Marker').removeAttr('disabled');
    $('#segmentation-nullBtn').removeClass('disabled').removeClass('disable-clicks');
    $('#segmentation-submitBtn').removeClass('disabled').removeClass('disable-clicks');
    $('#segmentation-audio-progress').prop('disabled', false);
    $('#playStimulusBtn').removeAttr('disabled');

    $('#evaluationNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');

}


Segmentation.prototype.createStimulusMap = function (conditionIndex) {
    var i;
    this.stimulusMap = []
    for (i = 0; i < this.config.conditions[conditionIndex]['stimulusKeys'].length; i++) {
        this.stimulusMap[i] = this.prependGroupID(this.config.conditions[conditionIndex]['stimulusKeys'][i],
            conditionIndex);
    }
    var referenceKeys = [];
    for (i = 0; i < this.config.conditions[conditionIndex]['referenceKeys'].length; i++) {
        referenceKeys.push(this.prependGroupID(this.config.conditions[conditionIndex]['referenceKeys'][i],
            conditionIndex));
    }

    this.audioGroup.setSyncIDs(this.stimulusMap.concat(referenceKeys));
};


// save the ratings for the current condition
Segmentation.prototype.saveRatings = function() {
    // make sure something was selected

    if (this.segmentVal === null) {
        alert('Press "Change heard" or "No change heard" button before continuing.');
        return false;
    }

    var stimulusMap = [];

    var i;
    var re = /G([0-9]+)_([a-zA-Z0-9]+)/;
    for (i = 0; i < this.stimulusMap.length; i++) {
        stimulusMap[i] = re.exec(this.stimulusMap[i])[2];
    }

    // save the selected one
    var conditionRatings = {};
    conditionRatings[stimulusMap[0]] = this.segmentVal;
    // conditionRatings[stimulusMap[1]] = this.segmentVal;

    // save the condition data
    this.completedConditionData[this.conditionIndex] = {'ratings': conditionRatings,
        'conditionID': this.config.conditions[this.conditionIndex].conditionID,
        'groupID': this.config.conditions[this.conditionIndex].groupID,
        'referenceFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['referenceFiles'],
        'stimulusFiles': this.config.conditionGroups[this.config.conditions[this.conditionIndex].groupID]['stimulusFiles'],
        'referenceKeys': this.config.conditions[this.conditionIndex].referenceKeys,
        'stimulusKeys': this.config.conditions[this.conditionIndex].stimulusKeys};

    return true;
};

Segmentation.prototype.audioOnTimeUpdate = function (e) {
    // var position;
    //
    // if (this.audioGroup.audioPlayingID == -1) {
    //
    // } else if (this.audioGroup.audioPlayingID == -2) {
    //     if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioSoloingID)) {
    //         position = e.target.currentTime / e.target.duration;
    //         if(position==1.0){
    //             position = 0.0;
    //         }
    //         $('#segmentation-audio-progress').val(position)
    //     }
    // } else {
    //     if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioPlayingID)) {
    //         position = e.target.currentTime / e.target.duration;
    //         if(position==1.0){
    //             position = 0.0;
    //         }
    //         $('#segmentation-audio-progress').val(position)
    //     }
    // }
};

Segmentation.prototype.audioProgressUpdate = function(audio){

    var position = +(audio.currentTime) / +(audio.duration);
    $('#segmentation-audio-progress').val(position)

};

Segmentation.prototype.audioOnPause = function(e){
    // var value = +($('#segmentation-audio-progress').val())
    var position
    if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioSoloingID)) {
        position = e.target.currentTime / e.target.duration;
    }else{
        position = e.target.currentTime / e.target.duration;
    }

    if(position>=1.0){
        $('#segmentation-audio-progress').val(0.0);
    }else{
        $('#segmentation-audio-progress').val(position);
    }
    clearInterval(this.audioUpdate);
};

Segmentation.prototype.changeTimeStamp = function(ID){
    clearInterval(this.audioUpdate)
    var audio = $('#' + this.audioGroup.ID + '_audio' + this.stimulusMap[ID]).get(0);
    var value = +($('#segmentation-audio-progress').val());

    audio.currentTime = audio.duration*value;
    this.audioUpdate = setInterval(this.audioProgressUpdate, 250, audio);
}