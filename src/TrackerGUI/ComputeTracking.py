# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 14:23:38 2021

@author: vajra
"""


import os
import holoviews as hv
import numpy as np
import pandas as pd
import LocationTracking_Functions as lt

from bokeh.plotting import show
hv.extension('bokeh','matplotlib')

# =========================================================================== #

def computeTracking(self, directory, paths, downsample, method):
    
    for i, path in enumerate(paths):
        
        video_dict = {
            'dpath'        : directory,  
            'file'         : os.path.basename(path),
            'start'        : 0, 
            'end'          : None,
            'region_names' : None, #['Left','Right']
            'dsmpl'        : downsample,
            'stretch'      : dict(width=1, height=1)
        }
        
        img_crp, video_dict = lt.LoadAndCrop(video_dict, cropmethod='Box')
        video_dict['reference'], img_ref = lt.Reference(video_dict, num_frames=50, frames=None) 
        
        tracking_params = {
            'loc_thresh'    : 99.5, 
            'use_window'    : True, 
            'window_size'   : 100, 
            'window_weight' : .9, 
            'method'        : 'dark',
            'rmv_wire'      : True, 
            'wire_krn'      : 5
        }
        
        location = lt.TrackLocation(self, video_dict, tracking_params)  
        location.to_csv(os.path.splitext(video_dict['fpath'])[0] + '_LocationOutput.csv', index=False)
        location.head()

        plt_trks = lt.showtrace(video_dict, location, color="red", alpha=.05, size=2)
        show(hv.render(plt_trks))