# -*- coding: utf-8 -*-
"""
computeFeature

computes a feature from the audio data
supported features are:
    'SpectralCentroid',
    'SpectralCrestFactor',
    'SpectralDecrease',
    'SpectralFlatness',
    'SpectralFlux',
    'SpectralKurtosis',
    'SpectralMfccs',
    'SpectralPitchChroma',
    'SpectralRolloff',
    'SpectralSkewness',
    'SpectralSlope',
    'SpectralSpread',
    'SpectralTonalPowerRatio',
    'TimeAcfCoeff',
    'TimeMaxAcf',
    'TimePeakEnvelope',
    'TimePredictivityRatio',
    'TimeRms',
    'TimeStd',
    'TimeZeroCrossingRate',
  Args:
      cFeatureName: feature to compute, e.g. 'SpectralSkewness'
      afAudioData: array with floating point audio data.
      f_s: sample rate
      afWindow: FFT window of length iBlockLength (default: hann)
      iBlockLength: internal block length (default: 4096 samples)
      iHopLength: internal hop length (default: 2048 samples)

  Returns:
      feature value v
      time stamp t
"""

import numpy as np
from scipy.signal import spectrogram
import matplotlib.pyplot as plt 
       
       
def computeFeature(cFeatureName, afAudioData, f_s, afWindow=None, iBlockLength=4096, iHopLength=2048):
    from ToolComputeHann import ToolComputeHann

    mypackage = __import__('Feature' + cFeatureName)
    hFeatureFunc = getattr(mypackage, 'Feature' + cFeatureName)

    # pre-processing: downmixing 
    if afAudioData.ndim > 1:
        afAudioData = afAudioData.mean(axis=1)
    
    # pre-processing: normalization
    fNorm = np.max(np.abs(afAudioData));
    if fNorm != 0:
        afAudioData = afAudioData/fNorm
   
    # pad with block length zeros just to make sure it runs for weird inputs, too
    afAudioData = np.concatenate((afAudioData,np.zeros([iBlockLength,])),axis = 0)         

    if isSpectral(cFeatureName):
        # compute window function for FFT
        if afWindow is None:
            afWindow = ToolComputeHann(iBlockLength)
    
        assert(afWindow.shape[0] == iBlockLength), "parameter error: invalid window dimension"
        
        # in the real world, we would do this block by block...
        [f,t,X] = spectrogram(  afAudioData,
                                f_s,
                                afWindow,
                                iBlockLength,
                                iBlockLength - iHopLength,
                                iBlockLength,
                                False,
                                True,
                                'spectrum')
    
        # we just want the magnitude spectrum...
        X = np.sqrt(X/2)
    
        # compute instantaneous pitch chroma
        v = hFeatureFunc(X,f_s)
    
    if isTemporal(cFeatureName):
        [v,t] = hFeatureFunc(afAudioData, iBlockLength, iHopLength, f_s)
        #[v,t] = hFeatureFunc(afAudioData, iBlockLength, iHopLength, f_s, np.array([2, 3]))
        
    return (v,t)

#######################################################   
# helper functions
def isSpectral(cName):
    bResult = False
    if "Spectral" in cName: 
        bResult = True
        
    return (bResult) 

def isTemporal(cName):
    bResult = False
    if "Time" in cName: 
        bResult = True
        
    return (bResult)
 
    



def computeFeatureCl(cPath, cFeatureName, bPlotOutput = False):
    from ToolReadAudio import ToolReadAudio
  
    # read audio file
    [f_s,afAudioData] = ToolReadAudio(cPath)
    #afAudioData = np.sin(2*np.pi * np.arange(f_s*1)*440./f_s)
 
    # compute feature
    [v,t] = computeFeature(cFeatureName, afAudioData, f_s)

    # plot feature output
    if bPlotOutput:
        plt.plot(t,v)
        
    return (v,t)
    
if __name__ == "__main__":
    import argparse

    # add command line args and parse them    
    parser = argparse.ArgumentParser(description='Compute key of wav file')
    parser.add_argument('--infile', metavar='path', required=False,
                        help='path to input audio file')
    parser.add_argument('--featurename', metavar='string', required=False,
                        help='feature name in the format SpectralPitchChroma')
    parser.add_argument('--plotoutput', metavar='bool', required=False,
                        help='option to plot the output')
 
    # retrieve command line args
    cPath = parser.parse_args().infile
    cFeatureName = parser.parse_args().featurename
    bPlotOutput  = parser.parse_args().plotoutput
    
    #only for debugging
    if __debug__:
        if not cPath:
            cPath = "c:/temp/test.wav"
        if not cFeatureName:
            cFeatureName = "TimePeakEnvelope"
        if not bPlotOutput:
            bPlotOutput = True
    
    # call the function
    computeFeatureCl(cPath, cFeatureName, bPlotOutput)
