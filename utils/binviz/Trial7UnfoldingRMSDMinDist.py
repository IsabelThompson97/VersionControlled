# from __future__ import division, print_function
from __future__ import annotations

import numpy as np
from westpa.core.systems import WESTSystem
from westpa.core.binning import RectilinearBinMapper, RecursiveBinMapper

import logging
log = logging.getLogger(__name__)
log.debug('loading module %r' % __name__)

class System(WESTSystem):
    """WESTPA system definition (2D pcoord) with nested (recursive) binning.

    pcoord dimensions:
      0: RMSD
      1: MinDist

    Notes:
      - RectilinearBinMapper boundaries must be monotonically increasing.
      - RecursiveBinMapper.add_mapper(mapper, replaces_bin_at) expects a *coordinate tuple*
        that lies inside the bin to be replaced (not a bin index).
    """

    def initialize(self):
        self.pcoord_ndim = 2
        self.pcoord_len = 2
        self.pcoord_dtype = np.float64

        # -----------------------------------------------------------------
        # Outer Mapper: [RMSD],[MinDist]
        # Outer (coarse) 2D partition: 4 quadrants
        #   RMSD:    [0, 5) and [5, inf)
        #   MinDist: [0, 5) and [5, inf)
        
        '''         
             inf                                               
             +----------------------------+----------------------+
             |               0            |          1           |   
             |                            |                      |
             5 ---------------------------|----------------------
             |                            |                      |
             |               2            |          3           |
             +---------------------------------------------------+    
             0                            5                      inf
        '''
        rmsd_outer = [0.0, 5.0, float("inf")]
        mindist_outer = [0.0, 5.0, float("inf")]
        outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])


        # INITIAL MAPPERS #####################################################
        # -----------------------------------------------------------------
        # Ensure all bstates start in their own bin
        # Expect RMSD < 5, MinDist < 5

        # initial_RMSD = [0.0, 1.3] + [1.4 + 0.1 * i for i in range(10)] + [5.0]
        # initial_MinDist = [0.0, 1.8, 1.95, 1.975, 1.985, 1.995, 2.00, 2.05, 2.10, 2.20, 2.40, 2.60, 2.80, 3.0, 3.20, 3.40, 3.60, 3.80, 4.00, 5.00]
        # initial_mapper = RectilinearBinMapper([initial_RMSD, initial_MinDist])

        # rmsdQuad1 = [5.0, float("inf")]
        # mindistQuad1 = [5.0, float("inf")]
        # mapperQuad1 = RectilinearBinMapper([rmsdQuad1, mindistQuad1])

        # rmsdQuad3 = [5.0, float("inf")]
        # mindistQuad3 = [0.0, 5.0]
        # mapperQuad3 = RectilinearBinMapper([rmsdQuad3, mindistQuad3])

        # rmsdQuad0 = [0.0, 5.0]
        # mindistQuad0 = [5.0, float("inf")]
        # mapperQuad0 = RectilinearBinMapper([rmsdQuad0, mindistQuad0])
      
        # -----------------------------------------------------------------
        # QUAD2 #####################################################
        # Low RMSD, Low MinDist (fine bins) 
        # Only active map for first 20 iterations, until at least one segment > 5.0 in either dimension
        # rmsd_lowQuad2 = [0.0, 1.3] + [1.4 + 0.1 * i for i in range(16)] + [3,3.25,3.50,3.75,4.0,4.25,4.50,4.75,5.0]
        # mindist_lowQuad2 = [0.0, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0]
  

        # Reduce RMSD resolution in low RMSD for < 3, moderately reduce minDist resolution for dist < 5
        rmsd_lowQuad2 = [0.0,1,2,2.25,2.5,2.75,3,3.25,3.50,3.75,4.0,4.25,4.50,4.75,5.0]
        mindist_lowQuad2 = [0.0,2,2.25,2.5,2.75,3,3.25,3.50,3.75,4.0,4.25,4.50,4.75,5.0]
        mapperQuad2 = RectilinearBinMapper([rmsd_lowQuad2, mindist_lowQuad2])

        # QUAD0 #####################################################
        # Low RMSD, High MinDist (coarser bins; adjust as desired) Quad0
        # Start with higher RMSD resolution, reduce resolution as RMSD increases > 5.0; fine minDist resolution for dist < 5, coarser bins for dist > 5 
        rmsd_lowQuad0 = [0.0,1,2,2.25,2.5,2.75,3,3.25,3.50,3.75,4.0,4.25,4.50,4.75,5.0]
        mindist_highQuad0 = [5.0 + i*0.2 for i in range(11)] + [float("inf")]
        mapperQuad0 = RectilinearBinMapper([rmsd_lowQuad0, mindist_highQuad0])

        # QUAD3 #####################################################
        # High RMSD, Low MinDist (coarser bins; adjust as desired) Quad3
        # Start with lower RMSD resolution, increase resolution as RMSD increases > 5.
        # Moderate minDist resolution until popns reach > 5, then coarser bins for dist < 5
        rmsd_highQuad3 = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 10.0, float("inf")]
        mindist_lowQuad3 = [0.0, 2, 3, 4, 5.0]
        mapperQuad3 = RectilinearBinMapper([rmsd_highQuad3, mindist_lowQuad3])

        # QUAD1 #####################################################
        # High RMSD, High MinDist (coarser bins; adjust as desired) Quad1
        # Start with low RMSD and minDist resolution, increase resolution as flux increases
        rmsd_highQuad1 = [5.0, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 10.0, float("inf")]
        mindist_highQuad1 = [5.0 + i*0.2 for i in range(11)] + [float("inf")]
        mapperQuad1 = RectilinearBinMapper([rmsd_highQuad1, mindist_highQuad1])


        # ADD MAPPERS #####################################################
        # -----------------------------------------------------------------

        # Setup the recursive bin mapper
        self.bin_mapper = RecursiveBinMapper(outer_mapper)

        # -----------------------------------------------------------------
        # INITIAL MAPPER - First iteration only 
        # self.bin_mapper.add_mapper(initial_mapper, [2.5,2.5])
        self.bin_mapper.add_mapper(mapperQuad2, [2.5,2.5])
        self.bin_mapper.add_mapper(mapperQuad1, [7.5,7.5])
        self.bin_mapper.add_mapper(mapperQuad0, [2.5,7.5])
        self.bin_mapper.add_mapper(mapperQuad3, [7.5,2.5])

        # -----------------------------------------------------------------
        # Set the target counts for each bin
        self.bin_target_counts = np.full((self.bin_mapper.nbins,), 8, dtype=int)
        # -----------------------------------------------------------------