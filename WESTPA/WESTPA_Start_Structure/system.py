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
        self.pcoord_ndim = 1
        self.pcoord_len = 2
        self.pcoord_dtype = numpy.float64
        
        # Outer Mapper: [mindist],[rmsd]
        mapper_outer = RectilinearBinMapper([[0, 5, float('inf')],
                                             [0,6,float('inf')]])  # Initial outer binning

        # For the first iteration only
        # HighDist = RectilinearBinMapper([[5, float('inf')]])
        
        # High Distance Mapper 
        HighDist = RectilinearBinMapper([[5,7,10,12,15,17,20,22,25,27,30,32,35,37,40,41,42,43,44,45,float('inf')],
                                         [RMSD?  ])  # Bins for distances > 5
       
        # Low Distance Mapper
        LowDist = RectilinearBinMapper([[0,1,2,3,3.5,4,4.5,5]
                                               [ RMSD?  ]])  # Distances < 5

        # High RMSD Mapper 
        HighRMSD = RectilinearBinMapper([[ Dist?  ],
                                         [6,7,8,9,10,float('inf')]])  # Bins for RMSD > 6
       
        # Low RMSD Mapper
        LowRMSD = RectilinearBinMapper([[  Dist?   ],
                                        [0,0.25,0.5,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4,4.1,4.2,4.3,4.5,4.75,5,5.1,5.2,5.3,5.5,5.75,6]])  # RMSD < 6
        
        
        # Setup the recursive bin mapper
        self.bin_mapper = RecursiveBinMapper(mapper_outer)
        self.bin_mapper.add_mapper(HighDist, [10, rmsd?])
        self.bin_mapper.add_mapper(LowDist, [3, rmsd?])
        self.bin_mapper.add_mapper(HighRMSD, [ dist?, 7])
        self.bin_mapper.add_mapper(LowRMSD, [ dist?, 2])
       
        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), int)
        self.bin_target_counts[...] = 8

