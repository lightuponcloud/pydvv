import unittest

from dvvset import DVVSet, Clock


class TestDVVSet(unittest.TestCase):

    def setUp(self):
        self.dvvset = DVVSet()

    def test_join(self):
        A = self.dvvset.new("v1")
        A1 = self.dvvset.create(A, "a")

        B = self.dvvset.new_with_history(self.dvvset.join(A1), "v2")
        B1 = self.dvvset.update(B, A1, "b")

        self.assertEqual(self.dvvset.join(A), [])
        self.assertEqual(self.dvvset.join(A1), [["a", 1]])
        self.assertEqual(self.dvvset.join(B1), [["a", 1], ["b", 1]])

    def test_update(self):
        A0 = self.dvvset.create(self.dvvset.new("v1"), "a")
        A1 = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(A0),["v2"]), A0, "a")
        A2 = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(A1),["v3"]), A1, "b")
        A3 = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(A0),["v4"]), A1, "b")
        A4 = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(A0),["v5"]), A1, "a")

        import pdb;pdb.set_trace()
        self.assertEqual( A0 , [[["a",1,["v1"]]],[]])
        self.assertEqual( A1 , [[["a",2,["v2"]]],[]])
        self.assertEqual( A2 , [[["a",2,[]], ["b",1,["v3"]]],[]])
        self.assertEqual( A3 , [[["a",2,["v2"]], ["b",1,["v4"]]],[]])
        self.assertEqual( A4 , [[["a",3,["v5","v2"]]],[]])

    def test_sync(self):
        X   = [[["x",1,[]]],[]]
        A   = self.dvvset.create(self.dvvset.new("v1"),"a")
        Y   = self.dvvset.create(self.dvvset.new_list(["v2"]),"b")
        A1  = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A),["v2"]), "a")
        A3  = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A1),["v3"]), "b")
        A4  = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A1),["v3"]), "c")
        W   = [[["a",1,[]]],[]]
        Z   = [[["a",2,["v2","v1"]]],[]]
        self.assertEqual(
            self.dvvset.sync([W,Z]),
            [[["a",2,["v2"]]],[]]
        )
        self.assertEqual( self.dvvset.sync([W,Z]), self.dvvset.sync([Z,W]))
        self.assertEqual( self.dvvset.sync([A,A1]), self.dvvset.sync([A1,A]))
        self.assertEqual( self.dvvset.sync([A4,A3]), self.dvvset.sync([A3,A4]))
        self.assertEqual( self.dvvset.sync([A4,A3]), [[["a",2,[]], ["b",1,["v3"]], ["c",1,["v3"]]],[]])
        self.assertEqual( self.dvvset.sync([X,A]), [[["a",1,["v1"]],["x",1,[]]],[]])
        self.assertEqual( self.dvvset.sync([X,A]), self.dvvset.sync([A,X]))
        self.assertEqual( self.dvvset.sync([X,A]), self.dvvset.sync([A,X]))
        self.assertEqual( self.dvvset.sync([A,Y]), [[["a",1,["v1"]],["b",1,["v2"]]],[]])
        self.assertEqual( self.dvvset.sync([Y,A]), self.dvvset.sync([A,Y]))
        self.assertEqual( self.dvvset.sync([Y,A]), self.dvvset.sync([A,Y]))
        self.assertEqual( self.dvvset.sync([A,X]), self.dvvset.sync([X,A]))

    def test_sync_update(self):
        # Mary writes v1 w/o VV
        A0  = self.dvvset.create(self.dvvset.new_list(["v1"]), "a")
        # Peter reads v1 with version vector (VV)
        VV1 = self.dvvset.join(A0)
        # Mary writes v2 w/o VV
        A1  = self.dvvset.update(self.dvvset.new_list(["v2"]), A0, "a")
        # Peter writes v3 with VV from v1
        A2  = self.dvvset.update(self.dvvset.new_list_with_history(VV1,["v3"]), A1, "a")
        self.assertEqual( VV1 , [["a",1]] )
        self.assertEqual( A0  , [[["a",1,["v1"]]],[]] )
        self.assertEqual( A1  , [[["a",2,["v2","v1"]]],[]] )
        # now A2 should only have v2 and v3, since v3 was causally newer than v1
        self.assertEqual( A2  , [[["a",3,["v3","v2"]]],[]] )

    def test_event(self):
        [A,_] = self.dvvset.create(self.dvvset.new("v1"),"a")
        self.assertEqual(
            self.dvvset.event(A,"a","v2"),
            [["a",2,["v2","v1"]]]
        )
        self.assertEqual(
            self.dvvset.event(A,"b","v2"),
            [["a",1,["v1"]], ["b",1,["v2"]]]
        )

    def test_less(self):
        A  = self.dvvset.create(self.dvvset.new_list("v1"),["a"])
        B  = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A),["v2"]), "a")
        B2 = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A),["v2"]), "b")
        B3 = self.dvvset.create(self.dvvset.new_list_with_history(self.dvvset.join(A),["v2"]), "z")

        C  = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(B),["v3"]), A, "c")

        D  = self.dvvset.update(self.dvvset.new_list_with_history(self.dvvset.join(C),["v4"]), B2, "d")
        self.assertTrue( self.dvvset.less(A,B) )
        self.assertTrue( self.dvvset.less(A,C) )
        self.assertTrue( self.dvvset.less(B,C) )
        self.assertTrue( self.dvvset.less(B,D) )
        self.assertTrue( self.dvvset.less(B2,D) )
        self.assertTrue( self.dvvset.less(A,D) )
        self.assertFalse( self.dvvset.less(B2,C) )
        self.assertFalse( self.dvvset.less(B,B2) )
        self.assertFalse( self.dvvset.less(B2,B) )
        self.assertFalse( self.dvvset.less(A,A) )
        self.assertFalse( self.dvvset.less(C,C) )
        self.assertFalse( self.dvvset.less(D,B2) )
        self.assertFalse( self.dvvset.less(B3,D) )

    def test_equal(self):
        A = Clock([["a",4,["v5","v0"]],["b",0,[]],["c",1,["v3"]]], ["v0"])
        B = Clock([["a",4,["v555","v0"]], ["b",0,[]], ["c",1,["v3"]]], [])
        C = Clock([["a",4,["v5","v0"]],["b",0,[]]], ["v6","v1"])
        # compare only the causal history
        self.assertTrue( self.dvvset.equal(A,B) )
        self.assertTrue( self.dvvset.equal(B,A) )
        self.assertFalse( self.dvvset.equal(A,C) )
        self.assertFalse( self.dvvset.equal(B,C) )

    def test_size(self):
        self.assertEqual( 1 , self.dvvset.size(self.dvvset.new_list(["v1"])) ),
        clock = Clock(
            [["a",4,["v5","v0"]],["b",0,[]],["c",1,["v3"]]],
            ["v4","v1"]
        )
        self.assertEqual( 5 , self.dvvset.size(clock) )

    def test_values(self):
        A = [[["a",4,["v0","v5"]],["b",0,[]],["c",1,["v3"]]], ["v1"]]
        B = [[["a",4,["v0","v555"]], ["b",0,[]], ["c",1,["v3"]]], []]
        C = [[["a",4,[]],["b",0,[]]], ["v1","v6"]]
        self.assertEqual( self.dvvset.ids(A), ["a","b","c"] )
        self.assertEqual( self.dvvset.ids(B), ["a","b","c"] )
        self.assertEqual( self.dvvset.ids(C), ["a","b"] )
        self.assertEqual( sorted(self.dvvset.values(A)), ["v0","v1","v3","v5"] )
        self.assertEqual( sorted(self.dvvset.values(B)), ["v0","v3","v555"] )
        self.assertEqual( sorted(self.dvvset.values(C)), ["v1","v6"] )

    def test_ids_values(self):
        A = [[["a",4,["v0","v5"]],["b",0,[]],["c",1,["v3"]]], ["v1"]]
        B = [[["a",4,["v0","v555"]], ["b",0,[]], ["c",1,["v3"]]], []]
        C = [[["a",4,[]],["b",0,[]]], ["v1","v6"]]
        self.assertEqual( self.dvvset.ids(A), ["a","b","c"] )
        self.assertEqual( self.dvvset.ids(B), ["a","b","c"] )
        self.assertEqual( self.dvvset.ids(C), ["a","b"] )
        self.assertEqual( sorted(self.dvvset.values(A)), ["v0","v1","v3","v5"] )
        self.assertEqual( sorted(self.dvvset.values(B)), ["v0","v3","v555"] )
        self.assertEqual( sorted(self.dvvset.values(C)), ["v1","v6"] )


if __name__ == '__main__':
    unittest.main()
