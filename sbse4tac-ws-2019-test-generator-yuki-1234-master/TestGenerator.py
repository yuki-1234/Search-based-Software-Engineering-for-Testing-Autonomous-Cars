import xml.etree.ElementTree as ET
import random
from os.path import dirname, join
from pathlib import Path


class TestGenerator:

    def getTest(self):
        x,y,w = -45,4,3.5

        tree = ET.parse('scenario/defaultcondition.xml')
        root = tree.getroot()
        ET.register_namespace('', 'http://drivebuild.com')
        for lanes in root.findall("{http://drivebuild.com}lanes"):
            for lane in lanes.findall("{http://drivebuild.com}lane"):
                for laneSegment in lane.findall("{http://drivebuild.com}laneSegment"):
                    print(laneSegment.tag, laneSegment.attrib)

        # Drop point
        item = ET.SubElement(lane,'laneSegment')
        item.attrib["x"] = str(x)
        item.attrib["y"] = str(y)
        item.attrib["width"] = str(w)

        # Generate straights  (x = -45 ~ -15
        for i in range(1,2):
            x += 10
            item = ET.SubElement(lane, "laneSegment")
            item.attrib["x"] = str(x)
            item.attrib["y"] = str(y)
            item.attrib["width"] = str(w)

        # Generate curves with random angle y += -2 ~ 2   (x = -25 ~ 85
        for i in range(2,15):
            x += 10
            y += random.uniform(-2, 2)
            item = ET.SubElement(lane, "laneSegment")
            item.attrib["x"] = str(x)
            item.attrib["y"] = str(y)
            item.attrib["width"] = str(w)

        # Generate straights until the goal point  (x = 85 ~ 120
        item = ET.SubElement(lane,"laneSegment")
        item.attrib["x"] = str(120)
        item.attrib["y"] = str(4)
        item.attrib["width"] = str(w)

        # Write XML code to mooseTest.dbe.xml
        tree.write('scenario/mooseTest.dbe.xml', encoding="UTF-8", xml_declaration=True, method="xml", short_empty_elements=True)

        ## TODO How DBC is generated or is this valid?
        return  (Path(join(dirname(__file__), "scenario/mooseTest.dbe.xml")), Path(join(dirname(__file__), "scenario/mooseTest.dbc.xml")))

    def print_test(self):
        # Print all of generated points
        tree = ET.parse('scenario/mooseTest.dbe.xml')
        root = tree.getroot()
        ET.register_namespace('', 'http://drivebuild.com')
        print("--Generated coordinates--")
        for lanes in root.findall("{http://drivebuild.com}lanes"):
            for lane in lanes.findall("{http://drivebuild.com}lane"):
                for laneSegment in lane.findall("{http://drivebuild.com}laneSegment"):
                    print(laneSegment.tag, laneSegment.attrib)


def main():
    from drivebuildclient.aiExchangeMessages_pb2 import VehicleID
    from drivebuildclient.AIExchangeService import AIExchangeService
    from dummy_ai import DummyAI

    service = AIExchangeService("localhost", 8383)

    test_generator = TestGenerator()
    test_case = test_generator.getTest()
    test_generator.print_test()

    environmnet = test_case[0]
    criteria = test_case[1]

    upload_result = service.run_tests("test", "test", environmnet, criteria)

    if upload_result and upload_result.submissions:
        for test_name, sid in upload_result.submissions.items():
            vid = VehicleID()
            vid.vid = "ego"
            DummyAI(service).start(sid, vid)


if __name__ == "__main__":
    main()
