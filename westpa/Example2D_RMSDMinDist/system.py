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

    RNA HAIRPIN FOLDING

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

        """
        -----------------------------------------------------------------
        Outer Mapper: [RMSD],[MinDist]
        
        Outer 2D partition: 4 quadrants
            RMSD:    [0, 10) and [10, inf)
            MinDist: [0, 10) and [10, inf)
        
      
             inf                                               
             +----------------------------+----------------------+
             |               0            |          1           |   
         D   |                            |                      |
         i  10 ---------------------------|----------------------
         s   |                            |                      |
         t   |               2            |          3           |
             +---------------------------------------------------+    
             0                            10                     inf
                                         RMSD

        -----------------------------------------------------------------
        """

        # OUTER MAPPERS ###########################################
        # -----------------------------------------------------------------
        rmsd_outer = [0.0, 10.0, float("inf")]
        mindist_outer = [0.0, 10.0, float("inf")]
        outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
        

        # INITIAL MAPPERS ###########################################
        # -----------------------------------------------------------------
        # Ensure all bstates start in their own bin
        # Expect RMSD > 10, MinDist > 35

        # initial_RMSD = [10,11,12,13,14,15,16,17,18,19,20, float('inf')]
        # initial_MinDist = [10 + i*1 for i in range(25)] + [float('inf')]
        # initial_mapper = RectilinearBinMapper([initial_RMSD, initial_MinDist])

        # rmsd_lowQuad2 = [0.0, 10.0]
        # mindist_lowQuad2 = [0.0, 10.0]
        # mapperQuad2 = RectilinearBinMapper([rmsd_lowQuad2, mindist_lowQuad2])

        # rmsd_highQuad3 = [10.0, float("inf")]
        # mindist_lowQuad3 = [0.0, 10.0]
        # mapperQuad3 = RectilinearBinMapper([rmsd_highQuad3, mindist_lowQuad3])

        # rmsd_lowQuad0 = [0.0, 10.0]
        # mindist_highQuad0 = [10.0, float("inf")]
        # mapperQuad0 = RectilinearBinMapper([rmsd_lowQuad0, mindist_highQuad0])


        # PHASE I MAPPERS :: Quad1 + Quad3 ################################
        # -----------------------------------------------------------------
        # Turn on ONLY Quad1, Quad3 for high RMSD (>10) to start, 
        # then add Quad0 and Quad2 for low RMSD (0-10) in later iterations.
        # Coarser bins for high RMSD to drive more reasonable MinDist values. 
        # Larger variation in ∆ MinDist > than ∆ RMSD per iteration at early stages, 
        # any change in RMSD driven by chain flexibility and end fluctuations.
        # Refine RMSD binning for MinDist < 15 or 20 to sample folding pathways more effectively.
        # -----------------------------------------------------------------
        
        # QUAD0 #####################################################
        # Low RMSD, High MinDist (coarser bins; adjust as desired) :: Quad 0
        # rmsd_lowQ0 = [0.0, 2.0, 4.0, 6.0, 8.0, 8.25, 8.5, 8.75, 9.0, 9.25, 9.5, 9.75, 10]
        # mindist_highQ0 = [10 + i*1 for i in range(16)] + [float("inf")]
        # mapperQuad0 = RectilinearBinMapper([rmsd_lowQ0, mindist_highQ0])
        
        # QUAD1 #####################################################
        # High RMSD, High MinDist (coarser bins; adjust as desired) :: Quad 1
        # rmsd_highQ1 = [10.0 + i*0.5 for i in range(7)] + [float("inf")]
        # mindist_highQ1 = [10 + i*0.2 for i in range(51)] + [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, float("inf")]
        # mapperQuad1 = RectilinearBinMapper([rmsd_highQ1, mindist_highQ1])
        
        # QUAD2 #####################################################
        # Low RMSD, Low MinDist (fine bins) :: Quad 2
        # rmsd_lowQ2 = [0.0,10.0]
        # mindist_lowQ2 = [0.0, 10]
        # mapperQuad2 = RectilinearBinMapper([rmsd_lowQ2, mindist_lowQ2])

        # QUAD3 #####################################################
        # High RMSD, Low MinDist (coarser bins; adjust as desired) :: Quad 3
        # rmsd_highQ3 = [10.0, 10.25, 10.5, 10.75, 11.0, 11.25, 11.5, 11.75, 12.0, 12.5, 13.0] + [float("inf")]
        # mindist_lowQ3 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10]
        # mapperQuad3 = RectilinearBinMapper([rmsd_highQ3, mindist_lowQ3])


        # PHASE II MAPPERS :: Quad2 Focus, pull from Quad0 + Quad3 ########
        # -----------------------------------------------------------------
        # 
        # 
        # 
        # 
        # 
        # -----------------------------------------------------------------

        # QUAD0 #####################################################
        # Low RMSD, High MinDist (coarser bins; adjust as desired) :: Quad 0
        # rmsd_lowQ0 = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.5, 9.0, 9.5, 10]
        # rmsd_lowQ0 = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10]
        rmsd_lowQ0 = [0.0, 2.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10]
        # mindist_highQ0 = [10 + i*1 for i in range(11)] + [float("inf")]
        # mindist_highQ0 = [10 + i*1 for i in range(6)] + [20, float("inf")]
        # mindist_highQ0 = [10, 15, 20, float("inf")]
        mindist_highQ0 = [10, float("inf")]
        mapperQuad0 = RectilinearBinMapper([rmsd_lowQ0, mindist_highQ0])
        
        
        # rmsd_lowQ0 = [0.0, 1.0, 1.5] + [2.0 + 0.1 * i for i in range(41)] + [6.2,6.4,6.6,6.8,7,7.25,7.5,7.75,8,8.25,8.5,8.75,9,9.25,9.5,9.75,10]
        # mindist_highQ0 = [10 + i*0.5 for i in range(21)] + [21, 22, 23, 24, 25, float("inf")]
        # mapperQuad0 = RectilinearBinMapper([rmsd_lowQ0, mindist_highQ0])
        
        # QUAD1 #####################################################
        # High RMSD, High MinDist (coarser bins; adjust as desired) :: Quad 1
        # rmsd_highQ1 = [10.0 + i*0.5 for i in range(5)] + [float("inf")]
        rmsd_highQ1 = [10.0, 11, 12] + [float("inf")]
        # mindist_highQ1 = [10 + i*1 for i in range(11)] + [float("inf")]
        # mindist_highQ1 = [10, 12.5, 15, float("inf")]
        mindist_highQ1 = [10, float("inf")]
        mapperQuad1 = RectilinearBinMapper([rmsd_highQ1, mindist_highQ1])

        # QUAD2 #####################################################
        # Low RMSD, Low MinDist (fine bins) :: Quad 2
        # rmsd_lowQ2 = [0.0,1,2,3,4,5,6,7,8,9,10]
        # mindist_lowQ2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10]
        # mapperQuad2 = RectilinearBinMapper([rmsd_lowQ2, mindist_lowQ2])

        #rmsd_lowQ2 = [0.0, 1.0, 1.5] + [2.0 + 0.1 * i for i in range(41)] + [6.2,6.4,6.6,6.8,7,7.25,7.5,7.75,8,8.25,8.5,8.75,9,9.25,9.5,9.75,10]
        # rmsd_lowQ2 = [0.0, 1.0, 1.5] + [2.0 + 0.1 * i for i in range(41)] + [6.2,6.4,6.6,6.8,7,7.25,7.5,7.75,8,8.5,9,9.5,10]
        # rmsd_lowQ2 = [0.0, 1.0, 1.5] + [2.0 + 0.05* i for i in range(81)] + [6.2,6.4,6.6,6.8,7,7.25,7.5,7.75,8,8.5,9,9.5,10]
        rmsd_lowQ2 = [0.0, 1.0, 1.5] + [2.0 + 0.1* i for i in range(41)] + [6.25,6.5,6.75,7,7.5,8,8.5,9,9.5,10]
        # mindist_lowQ2 = [0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.0, 9.0, 10]
        # mindist_lowQ2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10]
        mindist_lowQ2 = [0.0, 2.0, 4.0, 6.0, 8.0, 10]
        mapperQuad2 = RectilinearBinMapper([rmsd_lowQ2, mindist_lowQ2])

        # QUAD3 #####################################################
        # High RMSD, Low MinDist (coarser bins; adjust as desired) :: Quad 3
        # rmsd_highQ3 = [10.0, 10.5, 11, 11.5, 12] + [float("inf")]
        # rmsd_highQ3 = [10.0, 11, 12] + [float("inf")]
        rmsd_highQ3 = [10.0] + [float("inf")]
        mindist_lowQ3 = [0.0, 5.0, 10]
        mapperQuad3 = RectilinearBinMapper([rmsd_highQ3, mindist_lowQ3])


        # IMPLEMENT MAPPERS ################################################
        # -----------------------------------------------------------------
        # Set up the recursive bin mapper
        self.bin_mapper = RecursiveBinMapper(outer_mapper)

        # -----------------------------------------------------------------
        # Initial Mapper - First iteration only 
        # self.bin_mapper.add_mapper(initial_mapper, [15,15])
        
        self.bin_mapper.add_mapper(mapperQuad0, [5,15])
        self.bin_mapper.add_mapper(mapperQuad1, [15,15])
        self.bin_mapper.add_mapper(mapperQuad2, [5,5])
        self.bin_mapper.add_mapper(mapperQuad3, [15,5])

        
        # SET TARGET WALKER COUNT ######################################
        # -----------------------------------------------------------------
        self.bin_target_counts = np.full((self.bin_mapper.nbins,), 8, dtype=int)

