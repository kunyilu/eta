#!/usr/bin/env python
'''
Module that samples video frames.

Info:
    type: eta.core.types.Module
    version: 0.1.0

Copyright 2017-2018, Voxel51, LLC
voxel51.com

Brian Moore, brian@voxel51.com
'''
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *
# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

import logging
import os
import sys

import eta
from eta.core.config import Config
import eta.core.events as etae
import eta.core.module as etam
import eta.core.utils as etau
import eta.core.video as etav


logger = logging.getLogger(__name__)


class SampleConfig(etam.BaseModuleConfig):
    '''Sampler configuration settings.

    Attributes:
        data (DataConfig)
        parameters (ParametersConfig)
    '''

    def __init__(self, d):
        super(SampleConfig, self).__init__(d)
        self.data = self.parse_object_array(d, "data", DataConfig)
        self.parameters = self.parse_object(d, "parameters", ParametersConfig)


class DataConfig(Config):
    '''Data configuration settings.

    Inputs:
        input_path (eta.core.types.Video): The input video

    Outputs:
        output_path (eta.core.types.VideoFile):
            the path to the sampled video
    '''

    def __init__(self, d):
        self.input_path = self.parse_string(d, "input_path")
        self.output_path = self.parse_string(d, "output_path")


class ParametersConfig(Config):
    '''Parameter configuration settings.

    If `clips_path` is specified, it is used. Otherwise `fps` is used, with the
    native frame rate of the video being used if `fps` is also absent.

    Parameters:
        fps (eta.core.types.Number): [None] The output frame rate
        clips_path (eta.core.types.EventDetection): [None] Per-frame binary
            labels indicating which frames to sample
    '''

    def __init__(self, d):
        self.fps = self.parse_number(d, "fps", default=None)
        self.clips_path = self.parse_string(d, "clips_path", default=None)


def _sample_videos(sample_config):
    parameters = sample_config.parameters
    for data in sample_config.data:
        if parameters.clips_path:
            _sample_video_by_clips(data, parameters.clips_path)
        else:
            _sample_video_by_fps(data, parameters.fps)



def _sample_video_by_fps(data_config, fps):
    if fps:
        logger.info(
            "Sampling video %s at %s fps", data_config.input_path, fps)
    else:
        logger.info(
            "Sampling video %s at native frame rate ", data_config.input_path)

    etav.FFmpegVideoSampler(fps=fps).run(
        data_config.input_path, data_config.output_path)


def _sample_video_by_clips(data_config, clips_path):
    logger.info(
        "Sampling video %s by clips %s", data_config.input_path, clips_path)
    detections = etae.EventDetection.from_json(clips_path)
    frames = detections.to_series().to_str()
    file_end = "%05d.png"
    output_path = os.path.join(data_config.output_path, file_end)

    processor = etav.VideoProcessor(
        data_config.input_path,
        frames=frames,
        out_single_vidpath=output_path,
    )

    with processor:
        for img in processor:
            processor.write(img)


def _parse_output_path(data, allow_video_clips=False):
    nout = 0
    out_args = {}
    if data.output_frames_path:
        nout += 1
        out_args["out_impath"] = data.output_frames_path
    if data.output_frames_dir:
        nout += 1
        patt = eta.config.default_sequence_idx + eta.config.default_image_ext
        out_args["out_impath"] = os.path.join(data.output_frames_dir, patt)
    if data.output_video_path:
        nout += 1
        out_args["out_single_vidpath"] = data.output_video_path
    if data.output_video_clips_path:
        if not allow_video_clips:
            raise ValueError("Output 'output_video_clips_path' is not allowed")
        nout += 1
        out_args["out_vidpath"] = data.output_clips_path
    if nout > 1:
        raise ValueError("Only one output can be set")

    return out_args


def run(config_path, pipeline_config_path=None):
    '''Run the sample_videos module.

    Args:
        config_path: path to a SampleConfig file
        pipeline_config_path: optional path to a PipelineConfig file
    '''
    sample_config = SampleConfig.from_json(config_path)
    etam.setup(sample_config, pipeline_config_path=pipeline_config_path)
    _sample_videos(sample_config)


if __name__ == "__main__":
    run(*sys.argv[1:])
