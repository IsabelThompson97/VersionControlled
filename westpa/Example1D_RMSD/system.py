from __future__ import division, print_function
import os, sys, math, itertools
import numpy

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
        
        # Outer Mapper: [RMSD]
        rmsd_outer_bins = [0, 5, float('inf')]
        mapper_outer = RectilinearBinMapper([rmsd_outer_bins])  # Initial outer binning

        # For the first iteration only
        # HighRMSD = RectilinearBinMapper([[5, float('inf')]])

        # High RMSD Mapper I 
        # HighRMSD = RectilinearBinMapper([[5,5.5,6,6.5,7,7.5,8,8.25,8.5,8.75,9,9.1,9.25,9.3,9.4,9.5,9.6,9.75,9.8,10,10.1,10.25,10.3,10.4,10.5,10.6,10.75,10.8,11,11.25,11.5,11.75,12,12.25,12.5,12.75,13,14,15,float('inf')]])  # Bins for distances > 5
        # HighRMSD = RectilinearBinMapper([[5 + i*0.1 for i in range(20)]+ [7,7.5,8.0,9,10] + [float('inf')]])  # Bins for distances > 5

        # Low RMSD Mapper I - Run until pcoords < 5
        # LowRMSD = RectilinearBinMapper([[0,1,2,3,4,5]])

        # High RMSD Mapper II
        # Collapse bins > 5 by 0.5, 1 angstrom starting at 10 for every 25-50 iterations; 
        # Ex: 0.25 for 5-7 when lowest segment pcoord 3.75, collapse 8, 9, 10 into 1 angstrom 
        # HighRMSD = RectilinearBinMapper([[5 + i*0.25 for i in range(5)] + [6.5,7,8,10] + [float('inf')]])  # Bins for distances > 5
        # HighRMSD = RectilinearBinMapper([[5,5.5,6,6.5,7,8,10] + [float('inf')]])  # Bins for distances > 5
        # HighRMSD = RectilinearBinMapper([[5,6,8,10] + [float('inf')]])  # Bins for distances > 5
        # HighRMSD = RectilinearBinMapper([[5,10] + [float('inf')]])  # Bins for distances > 5
        highRMSD = [5] + [float('inf')]
        HighRMSD = RectilinearBinMapper([highRMSD])  # Bins for distances > 5

        # Low RMSD Mapper II
        # LowRMSD = RectilinearBinMapper([[0,1,2]+[3 + i*0.05 for i in range(41)]])
        # LowRMSD = RectilinearBinMapper([[0,0.5,1,1.5,]+[2 + i*0.05 for i in range(61)]])
        # LowRMSD = RectilinearBinMapper([[0,0.5,1,1.5,]+[2 + i*0.05 for i in range(40)] +[4 + i*0.1 for i in range(11)]])
        # LowRMSD = RectilinearBinMapper([[0,0.5,1,1.5,]+[2 + i*0.025 for i in range(40)] + [3 + i*0.05 for i in range(20)] + [4 + i*0.1 for i in range(11)]])
        # LowRMSD = RectilinearBinMapper([[0,0.5,1,1.5,]+[2 + i*0.025 for i in range(40)] + [3 + i*0.05 for i in range(20)] + [4 + i*0.2 for i in range(6)]])
        # LowRMSD = RectilinearBinMapper([[0,0.5,1,1.5,]+[2 + i*0.01 for i in range(50)] +[2 + i*0.005 for i in range(100)] + [3 + i*0.05 for i in range(20)] + [4, 4.5, 5]])
        # LowRMSD = RectilinearBinMapper([[0,1,1.5]+[1.6 + i*0.01 for i in range(40)] +[2 + i*0.005 for i in range(200)] + [3 + i*0.1 for i in range(10)] + [4, 4.5, 5]])
        lowRMSD = [0,1,1.5] + [1.6 + i*0.01 for i in range(40)] + [2 + i*0.005 for i in range(100)] + [2.5 + i*0.01 for i in range(50)] + [3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.5, 5]
        LowRMSD = RectilinearBinMapper([lowRMSD])  # Bins for distances < 5


        # Setup the recursive bin mapper
        self.bin_mapper = RecursiveBinMapper(mapper_outer)
        self.bin_mapper.add_mapper(HighRMSD, [10])
        self.bin_mapper.add_mapper(LowRMSD, [3])
       
        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), int)
        self.bin_target_counts[...] = 8


