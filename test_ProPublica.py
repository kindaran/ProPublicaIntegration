import unittest
import logging
import os
import sys

from ProPublica import getArgs
    
class TestArgs(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_pos_include_logging_level(self):
        sys.argv = ["app","path","file","debug"]
        self.assertEqual(len(getArgs()),3)
        self.assertEqual(getArgs()[2],"DEBUG")
        
    def test_pos_exclude_logging_level(self):
        sys.argv = ["app","path","file"]
        self.assertEqual(len(getArgs()),3)
        self.assertEqual(getArgs()[2],"INFO")
                
    def test_neg_not_enough_params(self):
        sys.argv = ["app","path"]
        self.assertEqual(getArgs(),None)
                
#END CLASS

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,format="%(levelname)s: %(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    logging.info("*****TEST START")  
    unittest.main()
    logging.info("*****TEST END")
# END IF
