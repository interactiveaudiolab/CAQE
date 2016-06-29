#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities module for pre-processing audio stimuli

Run on the command line, e.g.: ::

    $ python preprocess.py

.. note:: This module has dependencies not required by the CAQE web application. To install these dependencies, run
 ``pip install -r analysis_requirements.txt``.
"""
import argparse
import os

import numpy as np
import librosa


def rms_normalize(directory=None, file_list=None, suffix=None, target_rms=None):
    """
    This utility performs rms normalization on a directory or list of files. Note files must be WAV files.

    Parameters
    ----------
    directory : str
        Input directory of audio files to process. Either this or `file_list` must be defined. Default is None.
    file_list : list of str
        List of audio files to process. Either this or `directory` must be defined. Default is None.
    suffix : str
        The suffix to append to the output filenames. If `None`, then the input files will be overwritten. Default is
        None.
    target_rms : float
        The target RMS to which we normalize. If `None`, then calculate the minimum RMS of the peak normalized files
        and normalize to that.

    Returns
    -------
    output_file_list : list of str
    pre_norm_values : list of float
    post_norm_values : list of float
    """
    if file_list is None:
        if directory is None:
            raise Exception('Arguments `file_list` or `directory` must be defined')
        file_list = []

        for path, _dirs, files in os.walk(directory):
            file_list.extend([os.path.join(path, f) for f in files if os.path.splitext(f)[1] == ".wav" or
                              os.path.splitext(f)[1] == ".WAV"])
    pre_norm_values = np.asarray([_rms_of_file(file_name) for file_name in file_list])

    if target_rms is None:
        target_rms = min(pre_norm_values[pre_norm_values.nonzero()])

    if suffix is not None:
        output_file_list = []
        for f in file_list:
            head, tail = os.path.splitext(f)
            output_file_list.append(head + suffix + tail)
    else:
        output_file_list = file_list

    post_norm_values = np.asarray([_normalize_file(file_list[i],
                                                   output_file_list[i],
                                                   target_rms) for i in range(len(file_list))])

    return file_list, pre_norm_values, post_norm_values


def _rms_of_file(file_path, min_val=0.001, normalize=True):
    """
    Calculate the RMS of a file.

    Parameters
    ----------
    file_path : str
        File path of the input file.
    min_val : float
        When calculating the RMS, the signal will be bounded by the active region that is above this `min_val`
        threshold. Default is 0.001.
    normalize : bool
        Peak normalize before calculating the RMS. Default is True.

    Returns
    -------
    rms : float

    """
    x, _ = librosa.load(file_path, sr=None, mono=True)

    if normalize:
        divisor = np.max(np.abs(x))
        if divisor == 0:
            return 0
        x /= divisor

    idx = np.where(np.abs(x) > min_val)[0]
    x = np.power(x[min(idx):max(idx)], 2)

    return np.sqrt(np.mean(x))


def _normalize_file(input_file_path, output_file_path, target_rms):
    """
    Normalize the audio file at `input_file_path` to root mean square `target_rms` and save at `output_file_path` as a
     .WAV file.

    Parameters
    ----------
    input_file_path : str
        Input audio file path of audio to be read and normalized
    output_file_path : str
        Output audio file path to where the output audio file should be saved
    target_rms : float
        The target RMS value of the audio file, i.e. we normalize to this value.

    Returns
    -------
    post_norm_rms : float
        The RMS value after normalizing
    """
    x, sr = librosa.load(input_file_path, sr=None, mono=True)

    x_rms = np.sqrt(np.mean(np.power(x, 2)))
    y = x * (target_rms / x_rms)

    librosa.output.write_wav(output_file_path, y, sr, norm=False)

    return np.sqrt(np.mean(np.power(y, 2)))


def generate_source_separation_anchors(directory=None, file_list=None):
    """
    Generate the PEASS-style anchors for use in a source separation evaluation.

    "The distorted target anchor is created by low-pass filtering the target source signal to a 3.5 kHz cut-off
    frequency and by randomly setting 20% of the remaining timefrequency coefficients to zero."

    "The artifacts anchor is ... created by randomly setting 99% of the time-frequency coefficients of the target to
    zero and by adjusting the loudness of the resulting signal to that of the target." - Note that we simply used RMS
    instead of the ISO 352B loudness model as discussed in the paper.

    Parameters
    ----------
    directory : str
        Input directory of audio files to process. Either this or `file_list` must be defined. Default is None.
    file_list : list of str
        List of audio files to process. Either this or `directory` must be defined. Default is None.

    Returns
    -------
    None

    References
    ----------
    .. [1] Emiya, V., et al. Subjective and Objective Quality Assessment of Audio Source Separation. IEEE Transactions
     on Audio, Speech, and Language Processing, 19(7): 2046-2057, 2011.
    """
    if file_list is None:
        if directory is None:
            raise Exception('Arguments `file_list` or `directory` must be defined')
        file_list = []

        for path, _dirs, files in os.walk(directory):
            file_list.extend([os.path.join(path, f) for f in files if os.path.splitext(f)[1] == ".wav" or
                              os.path.splitext(f)[1] == ".WAV"])

    for input_file_name in file_list:
        x, sr = librosa.load(input_file_name, sr=None, mono=False)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        n_fft = int(2**np.round(np.log2(sr * 0.046)))

        # distorted target anchor
        X = [librosa.stft(x[i], n_fft=n_fft, hop_length=n_fft/2) for i in range(x.shape[0])]
        cutoff = int(np.ceil((3500.0/sr) * n_fft))
        for _X in X:
            _X[cutoff:, :] = 0.0
            _X[:, np.random.random(_X.shape[1]) <= 0.2] = 0.0
        x_anch1 = np.array([librosa.istft(_X, hop_length=n_fft/2) for _X in X])

        if x_anch1.shape[0] == 1:
            x_anch1 = x_anch1.reshape(-1)
        output_file_name = os.path.splitext(input_file_name)[0] + '_anchorDistTarget' + '.wav'
        librosa.output.write_wav(output_file_name, x_anch1, sr=sr)

        # artificial noise anchor
        x_mono = np.mean(x, axis=0)
        X = librosa.stft(x_mono, n_fft=n_fft, hop_length=n_fft/2)
        X[np.random.random(X.shape) <= 0.99] = 0.0
        artifacts = librosa.istft(X, hop_length=n_fft/2)
        artifacts_rms = np.sqrt(np.mean(np.power(artifacts, 2)))
        x_rms = np.sqrt(np.mean(np.power(x, 2)))
        artifacts *= (x_rms / artifacts_rms)
        if x.shape[0] == 1:
            artifacts = artifacts.reshape(1, -1)
        elif x.shape[0] == 2:
            artifacts = np.array([artifacts, artifacts])
        else:
            raise Exception('More than 2 channels.')
        artifacts_pad = np.zeros_like(x)
        artifacts_pad[:artifacts.shape[0], :artifacts.shape[1]] = artifacts
        x_anch2 = x + artifacts_pad

        if x_anch2.shape[0] == 1:
            x_anch2 = x_anch2.reshape(-1)
        output_file_name = os.path.splitext(input_file_name)[0] + '_anchorArtif' + '.wav'
        librosa.output.write_wav(output_file_name, x_anch2, sr=sr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-process audio stimuli.')
    sp = parser.add_subparsers(dest='command')

    ch = sp.add_parser('rms-normalize', help='RMS normalize .wav files in a directory.')
    ch.add_argument('input_directory', type=str, help='Path to input directory')
    ch.add_argument('--suffix', type=str, help='The suffix to append to the normalized files. If none is given, the '
                                             'input files will be overwritten.', default=None)
    ch.add_argument('--target-rms', type=float, help='The target rms value. If none is given, it will calculate the '
                                                     'max possible without clipping.', default=None)

    ch = sp.add_parser('generate-ss-anchors', help='Generate anchors for source separation given a directory of '
                                                   '.wav files.')
    ch.add_argument('input_directory', type=str, help='Path to the input directory')

    args = parser.parse_args()

    if args.command == 'rms-normalize':
        rms_normalize(args.input_directory, suffix=args.suffix, target_rms=args.target_rms)
    elif args.command == 'generate-ss-anchors':
        generate_source_separation_anchors(args.input_directory)