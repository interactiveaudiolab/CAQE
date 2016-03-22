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

    this.state = EvaluationTaskStateEnum.INTRODUCTION;
    this.currentView = this.views[this.state];
    this.conditionIndex = 0;
    this.completedConditionData = [];

    this.loadTrainingAudio();
    this.loadConditionAudio(this.conditionIndex);

    var evaluationTaskHandle = this;
    window.onbeforeunload = function () {
        if (evaluationTaskHandle.state !== EvaluationTaskStateEnum.COMPLETE) {
            return 'The evaluation is not complete. Are you sure you want to leave?';
        }
    }
};


EvaluationTask.prototype.views = [
    '#introduction',
    '#training',
    '#evaluation',
    '#submit',
    '#complete',
    '#error',
    '#loading'];


EvaluationTask.prototype.showOnly = function (targetView) {
    for (var i=0; i < this.views.length; i++) {
        if (this.views[i] !== targetView) {
            $(this.views[i]).addClass('hidden');
        }
    }

    $(targetView).removeClass('hidden');
};


EvaluationTask.prototype.audioOnTimeUpdate = function (e) {
    if (this.audioGroup.audioPlayingID == -1) {
        $('#playback-position').val(0);
    } else if (this.audioGroup.audioPlayingID == -2) {
        if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioSoloingID)) {
            var position = e.target.currentTime / e.target.duration * 100;
            $('#playback-position').val(position);
        }
    } else {
        if (e.srcElement.id==(this.audioGroup.ID + '_audio' + this.audioGroup.audioPlayingID)) {
            var position = e.target.currentTime / e.target.duration * 100;
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


EvaluationTask.prototype.loadConditionAudio = function (conditionIndex) {
    var key;
    for (key in this.config.conditions[conditionIndex]['referenceFiles']) {
        if (this.config.conditions[conditionIndex]['referenceFiles'].hasOwnProperty(key)) {
            this.addAudio(this.audioGroup, this.config.conditions[conditionIndex]['referenceFiles'][key], key);
        }
    }
    for (key in this.config.conditions[conditionIndex]['stimulusFiles']) {
        if (this.config.conditions[conditionIndex]['stimulusFiles'].hasOwnProperty(key)) {
            this.addAudio(this.audioGroup, this.config.conditions[conditionIndex]['stimulusFiles'][key], key);
        }
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
    this.audioGroup.play(ID);
    $('.play-btn').removeClass('btn-success').addClass('btn-default disabled disable-clicks');
    $('#playReference' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played');
};


EvaluationTask.prototype.playStimulus = function(idx) {
    this.audioGroup.play(this.stimulusMap[idx]);
    $('.play-btn').removeClass('btn-success').addClass('btn-default disabled disable-clicks');
    $('#playStimulus' + idx + 'Btn').removeClass('btn-default').addClass('btn-success played');
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
    var i = 0;
    for (var key in this.config.conditions[conditionIndex]['stimulusFiles']) {
        if (this.config.conditions[conditionIndex]['stimulusFiles'].hasOwnProperty(key)) {
            this.stimulusMap[i] = key;
            i++;
        }
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


MushraTask.prototype.nextTrial = function () {
    if (EvaluationTask.prototype.nextTrial.apply(this)) {
        this.createStimulusMap(this.conditionIndex);
    }
};


// save the ratings for the current condition
MushraTask.prototype.saveRatings = function() {
    conditionRatings = {};
    stimulusMap = this.stimulusMap;
    $('.mushra-slider').each( function(idx) {
        conditionRatings[stimulusMap[idx]] = this.value;
    });

    this.completedConditionData[this.conditionIndex] = {'ratings': conditionRatings,
        'conditionID': this.config.conditions[this.conditionIndex].conditionID,
        'referenceFiles': this.config.conditions[this.conditionIndex].referenceFiles,
        'stimulusFiles': this.config.conditions[this.conditionIndex].stimulusFiles};
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
    this.comparisonIndex = 0;
    this.conditionRatings = {};
    this.timeoutPassed = false;
    this.createStimulusMap(this.conditionIndex, this.comparisonIndex);
}

PairwiseTask.prototype.startEvaluation = function () {
    EvaluationTask.prototype.startEvaluation.apply(this);

    this.setComparisonCountLabels();
    this.audioGroup.setLoopAudio(true);
};


PairwiseTask.prototype.setComparisonCountLabels = function () {
    $('#currentComparisonLbl').html(this.comparisonIndex + 1);
    $('#totalComparisonsLbl').html(this.config.conditions[this.conditionIndex]['comparisonPairs'].length);
};

PairwiseTask.prototype.testTimeoutCallback = function (_this) {
    _this.timeoutPassed = true;
    _this.testNextComparisonConditions();
};


PairwiseTask.prototype.playReference = function(ID) {
    this.audioGroup.solo(ID);
    if (this.audioGroup.audioPlayingID == -1) {
        this.audioGroup.syncPlay();
    }

    $('.play-btn').removeClass('btn-success').addClass('btn-default');
    $('#playReference' + ID + 'Btn').removeClass('btn-default').addClass('btn-success played');

    this.testNextComparisonConditions();
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

    this.testNextComparisonConditions();
};


PairwiseTask.prototype.stopAllAudio = function() {
    this.audioGroup.syncPause();
    $('.play-btn').removeClass('btn-success').addClass('btn-default');
};


PairwiseTask.prototype.nextComparison = function () {
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

    this.comparisonIndex++;
    if (this.comparisonIndex >= this.config.conditions[this.conditionIndex]['comparisonPairs'].length) {
        $(window).scrollTop();
        this.nextTrial();
    } else {
        this.createStimulusMap(this.conditionIndex, this.comparisonIndex);
        this.setComparisonCountLabels();
        this.timeoutPassed = false;
        this.testTimeout = setTimeout(this.testTimeoutCallback, this.config['testTimeoutSec'] * 1000.0, this);
    }
};


PairwiseTask.prototype.testNextComparisonConditions = function () {
    var qry = $('#evaluation');
    var all_played = qry.find('.play-btn').length == qry.find('.play-btn').filter('.played').length;
    var stimulus_selected = $('.pairwise-stimulus-play-btn').hasClass('pairwise-selected');

    if (all_played && stimulus_selected && this.timeoutPassed) {
        $('#evaluationNextBtn').removeClass('disable-clicks').parent().removeClass('disabled');
    }
};


PairwiseTask.prototype.nextTrial = function () {
    // save the condition ratings list
    this.completedConditionData[this.conditionIndex] = {'ratings': this.conditionRatings,
        'conditionID': this.config.conditions[this.conditionIndex].conditionID,
        'referenceFiles': this.config.conditions[this.conditionIndex].referenceFiles,
        'stimulusFiles': this.config.conditions[this.conditionIndex].stimulusFiles};

    // clear variables
    this.comparisonIndex = 0;
    this.conditionRatings = [];

    this.conditionIndex++;
    if (this.conditionIndex >= this.config.conditions.length) {
        this.submitResults();
    } else {
        this.createStimulusMap(this.conditionIndex, this.comparisonIndex);
        this.setComparisonCountLabels();
        this.timeoutPassed = false;
        this.testTimeout = setTimeout(this.testTimeoutCallback, this.config['testTimeoutSec'] * 1000.0, this);
    }
};


PairwiseTask.prototype.createStimulusMap = function (conditionIndex, comparisonIndex) {
    this.stimulusMap = this.config.conditions[conditionIndex]['comparisonPairs'][comparisonIndex];
    this.referenceNames = Object.keys(this.config.conditions[conditionIndex]['referenceFiles']);

    this.audioGroup.setSyncIDs(this.stimulusMap.concat(this.referenceNames));
};


// save the ratings for the current condition
PairwiseTask.prototype.saveRatings = function() {
    // make sure something was selected
    if (!$('.pairwise-stimulus-play-btn').hasClass('pairwise-selected')) {
        alert('Press the A or B button to select your preferred recording before continuing.');
        return false;
    }

    // save the selected one
    var selected = $('playStimulus0Btn').hasClass('pairwise-selected') ? 'A' : 'B';
    this.conditionRatings[this.comparisonIndex] = {'stimuli': this.stimulusMap,
        'selection': selected};

    return true;
};