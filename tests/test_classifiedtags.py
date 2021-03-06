# Created: 21.07.2012, taken from my ezdxf project
# Copyright (C) 2012, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from io import StringIO
from dxfgrabber.tags import Tags, DXFTag
from dxfgrabber.tags import ClassifiedTags

class TestClassifiedTags(unittest.TestCase):
    def setUp(self):
        self.xtags = ClassifiedTags.from_text(XTAGS1)

    def test_init_appdata(self):
        self.assertIsNotNone(self.xtags.get_appdata('{ACAD_XDICTIONARY'))

    def test_init_with_tags(self):
        tags = Tags.from_text(XTAGS1)
        xtags = ClassifiedTags(tags)
        self.assertEqual(3, len(xtags.subclasses))
        self.assertEqual(1, len(xtags.xdata))

    def test_init_xdata(self):
        self.assertIsNotNone(self.xtags.get_xdata('RAK'))

    def test_appdata_content_count(self):
        xdict = self.xtags.get_appdata('{ACAD_XDICTIONARY')
        self.assertEqual(3, len(xdict))

    def test_appdata_content(self):
        xdict = self.xtags.get_appdata('{ACAD_XDICTIONARY')
        self.assertEqual(xdict.get_value(360), "63D5")

    def test_tags_skips_appdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.noclass.get_value(360)

    def test_xdata_content_count(self):
        rak = self.xtags.get_xdata('RAK')
        self.assertEqual(17, len(rak))

    def test_tags_skips_xdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.noclass.get_value(1000)

    def test_getitem_layer(self):
        self.assertEqual(self.xtags.noclass[0], DXFTag(0, 'LAYER'))

    def test_getitem_xdict(self):
        self.assertEqual(self.xtags.noclass[2], DXFTag(102, 0))

    def test_getitem_parent(self):
        self.assertEqual(self.xtags.noclass[3], DXFTag(330, '18'))

    def test_get_last_item(self):
        self.assertEqual(self.xtags.noclass[-1], DXFTag(330, '18'))

    def test_tagscount(self):
        """ apdata counts as one tag and xdata counts as one tag. """
        self.assertEqual(4, len(self.xtags.noclass))

    def test_subclass_AcDbSymbolTableRecord(self):
        subclass = self.xtags.get_subclass('AcDbSymbolTableRecord')
        self.assertEqual(1, len(subclass))

    def test_subclass_AcDbLayerTableRecord(self):
        subclass = self.xtags.get_subclass('AcDbLayerTableRecord')
        self.assertEqual(8, len(subclass))

XTAGS1 = """  0
LAYER
  5
7
102
{ACAD_XDICTIONARY
360
63D5
102
}
330
18
100
AcDbSymbolTableRecord
100
AcDbLayerTableRecord
  2
0
 70
0
 62
7
  6
CONTINUOUS
370
-3
390
8
347
805
1001
RAK
1000
{75-LANGENSCHNITT-14
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LANGENSCHNITT-14}
1000
{75-LANGENSCHNITT-2005
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LANGENSCHNITT-2005}
"""
class TestXDATA(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(XTAGS2)

    def test_xdata_count(self):
        self.assertEqual(3, len(self.tags.xdata))

    def test_tags_count(self):
        """ 3 xdata chunks and two 'normal' tag. """
        self.assertEqual(2, len(self.tags.noclass))

    def test_xdata3_tags(self):
        xdata = self.tags.get_xdata('XDATA3')
        self.assertEqual(xdata[0], DXFTag(1001, 'XDATA3'))
        self.assertEqual(xdata[1], DXFTag(1000, 'TEXT-XDATA3'))
        self.assertEqual(xdata[2], DXFTag(1070, 2))
        self.assertEqual(xdata[3], DXFTag(1070, 3))

XTAGS2 = """  0
LAYER
  5
7
1001
RAK
1000
TEXT-RAK
1070
1
1070
1
1001
MOZMAN
1000
TEXT-MOZMAN
1070
2
1070
2
1001
XDATA3
1000
TEXT-XDATA3
1070
2
1070
3
"""


class Test2xSubclass(unittest.TestCase):
    def setUp(self):
        self.tags = ClassifiedTags.from_text(SPECIALCASE_TEXT)

    def test_read_tags(self):
        subclass2 = self.tags.get_subclass('AcDbText')
        self.assertEqual(DXFTag(100, 'AcDbText'), subclass2[0])

    def test_key_error(self):
        with self.assertRaises(KeyError):
            self.tags.get_subclass('AcDbMozman')

    def test_skip_empty_subclass(self):
        self.tags.subclasses[1] = Tags()
        subclass2 = self.tags.get_subclass('AcDbText')
        self.assertEqual(DXFTag(100, 'AcDbText'), subclass2[0])

SPECIALCASE_TEXT = """  0
TEXT
  5
8C9
330
6D
100
AcDbEntity
  8
0
100
AcDbText
 10
4.304757059922736
 20
1.824977382542784
 30
0.0
 40
0.125
  1
Title:
 41
0.85
  7
ARIALNARROW
"""
