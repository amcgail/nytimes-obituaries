import unittest

class testCoding(unittest.TestCase):

    def test_basics(self):


        # the MongoDB works and can load at least one document
        import occ
        coder = occ.Coder()
        search_results = occ.db.find({}).limit(1)

        results = list(coder.loadFromMongoAttributes( search_results ))
        assert( len(results) > 0 )

if __name__ == '__main__':
    unittest.main()