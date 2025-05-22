from __future__ import division, print_function
import os, sys, math, itertools
import numpy
import westpa
from westpa.core.systems import WESTSystem
from westpa.core.binning import RectilinearBinMapper
from westpa.core.binning import RecursiveBinMapper

import logging
log = logging.getLogger(__name__)
log.debug('loading module %r' % __name__)


class System(WESTSystem):
    def initialize(self):
        self.pcoord_ndim = 2
        self.pcoord_len = 2
        self.pcoord_dtype = numpy.float64

        # -----------------------------------------------------------------
        # Outer Mapper: [eRMSD],[RoG]
        # Bins:
        # (0,0): eRMSD in [0,1), RoG in [0,5)
        # (0,1): eRMSD in [0,1), RoG in [5,inf)
        # (1,0): eRMSD in [1,inf), RoG in [0,5)
        # (1,1): eRMSD in [1,inf), RoG in [5,inf)
        mapper_outer = RectilinearBinMapper([[0, 1, float('inf')],
                                             [0, 5 , float('inf')]])

        # -----------------------------------------------------------------
        # Initial mapper - first iteration only
        # initial_mapper = RectilinearBinMapper([[1,1.5,1.6,1.7,1.8,1.9,2.0,float('inf')],
        #                                       [5,10,11,12,13,14,15,16,17,18,19,20,float('inf')]])

        # -----------------------------------------------------------------
        # Refined mappers for specific regions (quadrants defined by outer_mapper)

        # Region 1: eRMSD < 1, RoG < 5 (Outer bin (0,0))
        # Refines the [0,1) eRMSD range and [0,5) RoG range.
        # Low_eRMSD_LowRoG = RectilinearBinMapper([[0,0.5,0.7,1],
        #                                          [0,0.5,1,1.5,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,4.75,5]])

        # Region 2: eRMSD < 1, RoG > 5 (Outer bin (0,1))
        # Refines the [0,1) eRMSD range and [5,inf) RoG range.
        # Low_eRMSD_HighRoG = RectilinearBinMapper([[0,0.5,0.7,1],
        #                                           [5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,20,float('inf')]])
        
        # Region 3: eRMSD > 1, RoG < 5 (Outer bin (1,0))
        # Refines the [1,inf) eRMSD range and [0,5) RoG range.
        # High_eRMSD_LowRoG = RectilinearBinMapper([[1.0,1.1,1.11,1.12,1.13,1.14,1.15,1.16,1.17,1.18,1.19,1.2,1.21,1.22,1.23,1.24,1.25,1.26,1.27,1.28,1.29,1.3,1.31,1.32,1.33,1.34,1.35,1.36,1.37,1.38,1.39,1.4,1.41,1.42,1.43,1.44,1.45,1.46,1.47,1.48,1.49,1.5,1.51,1.52,1.53,1.54,1.55,1.56,1.57,1.58,1.59,1.6,1.61,1.62,1.63,1.64,1.65,1.66,1.67,1.68,1.69,1.7,1.71,1.72,1.73,1.74,1.75,1.8,float('inf')],
        #                                           [0,0.5,1,1.5,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.25,4.5,4.75,5]])

        # PHASE I - Region 4: eRMSD > 1, RoG > 5 (Outer bin (1,1))
        # Refines the [1.5,inf) eRMSD range and [5,inf) RoG range.
        High_eRMSD_HighRoG = RectilinearBinMapper([[1.0,1.5,1.51,1.52,1.53,1.54,1.55,1.56,1.57,1.58,1.59,1.6,1.61,1.62,1.63,1.64,1.65,1.66,1.67,1.68,1.69,1.7,1.71,1.72,1.73,1.74,1.75,1.76,1.77,1.78,1.79,1.8,1.81,1.82,1.83,1.84,1.85,1.86,1.87,1.89,1.9,1.95,2.0,float('inf')],
                                                   [5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15,16,18,20,float('inf')]])

        # -----------------------------------------------------------------
        # Setup the recursive bin mapper
        self.bin_mapper = RecursiveBinMapper(mapper_outer)
  
        # Add mappers to specific outer bins
        # self.bin_mapper.add_mapper(initial_mapper,       [1.5,7])
        # self.bin_mapper.add_mapper(Low_eRMSD_LowRoG,   [0.5,1]) 
        # self.bin_mapper.add_mapper(Low_eRMSD_HighRoG,  [0.5,7])
        # self.bin_mapper.add_mapper(High_eRMSD_LowRoG,  [1.5,2])
        self.bin_mapper.add_mapper(High_eRMSD_HighRoG, [1.5,7]) 
        
        # -----------------------------------------------------------------
        # Set the target counts for each bin
        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), int)
        self.bin_target_counts[...] = 8