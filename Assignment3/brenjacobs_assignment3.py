"""Assignment 3: Spatial Overlays and Areal Interpolation.
Complete three functions using ArcPy and pathlib.Path. Prepare and project
copies before analysis; preserve inputs and avoid hardcoded paths or values.
Check input paths, geometry types, fields, coordinate systems, and output names.
Use try/except handling to catch and report errors.
Find and download census boundaries, a census/ACS numeric attribute, and roads (or another dataset with line geometry).
"""


def hawkid():
    return ["Brennan Jacobs", "brenjacobs"]


# Problem 1 (20 points)
def prepare_data(input_fc, output_geodatabase, out_coordinate_system,
                 join_table=None, join_field=None, value_field=None):
    """Create or reuse the geodatabase; import and project one feature dataset.
    Use the input base name and return the prepared feature class path.
    For polygons, import a CSV's ID attribute and one numeric value
    and join that value using the join_field that . Supply all three join
    arguments together. Preserve inputs and reject existing output names.
    """
    pass

import arcpy
import csv
from pathlib import Path


def check_exists(path, label):
    if not arcpy.Exists(str(path)):
        raise ValueError(f"{label} not found: {path}")


def check_fields(fc, field_names):
    existing = [f.name.lower() for f in arcpy.ListFields(str(fc))]
    for name in field_names:
        if name.lower() not in existing:
            raise ValueError(f"Field '{name}' not found in {fc}")


def check_field_types(fc, field_name, allowed_types):
    for f in arcpy.ListFields(str(fc)):
        if f.name.lower() == field_name.lower():
            if f.type not in allowed_types:
                raise ValueError(
                    f"Field '{field_name}' is type {f.type}, expected {allowed_types}")


def check_shape_type(fc, expected, label):
    shape_type = arcpy.Describe(str(fc)).shapeType
    if shape_type != expected:
        raise ValueError(f"{label} must be {expected}, but it is {shape_type}")


def check_projected_meters(fc):
    sr = arcpy.Describe(str(fc)).spatialReference
    if sr.name == "Unknown":
        raise ValueError(f"{fc} has an unknown coordinate system")
    if sr.type != "Projected":
        raise ValueError(f"{fc} is not in a projected coordinate system")
    if sr.metersPerUnit != 1:
        raise ValueError(f"{fc} is not in meters")
    return sr.name


def check_output_location(output_fc):
    out = Path(output_fc)
    gdb = out.parent
    if gdb.suffix.lower() != ".gdb" or not gdb.exists():
        raise ValueError(f"Output geodatabase does not exist: {gdb}")
    if arcpy.Exists(str(out)):
        raise ValueError(f"Output already exists: {out}")

def prepare_data(input_fc, output_geodatabase, out_coordinate_system,
                 join_table=None, join_field=None, value_field=None):
    try:
        check_exists(input_fc, "Input feature class")
        in_sr = arcpy.Describe(str(input_fc)).spatialReference
        if in_sr.name == "Unknown":
            raise ValueError(f"{input_fc} has an unknown coordinate system")

        out_sr = arcpy.SpatialReference(out_coordinate_system)
        if out_sr.type != "Projected" or out_sr.metersPerUnit != 1:
            raise ValueError("out_coordinate_system must be projected, in meters")

        if join_table is not None:
            if join_field is None or value_field is None:
                raise ValueError("join_field and value_field are needed with join_table")
            if not Path(join_table).exists():
                raise ValueError(f"Join table not found: {join_table}")
            with open(join_table, "r", newline="", encoding="utf-8-sig") as source:
                header = csv.DictReader(source).fieldnames
            if join_field not in header or value_field not in header:
                raise ValueError(f"CSV must have columns '{join_field}' and '{value_field}'")
            check_fields(input_fc, [join_field])
            existing = [f.name.lower() for f in arcpy.ListFields(str(input_fc))]
            if value_field.lower() in existing:
                raise ValueError(f"'{value_field}' already exists in {input_fc}")

        #Step 2: create the geodatabase if it is not there yet
        gdb = Path(output_geodatabase)
        if gdb.suffix.lower() != ".gdb":
            raise ValueError("output_geodatabase must end in .gdb")
        if not gdb.exists():
            gdb.parent.mkdir(parents=True, exist_ok=True)
            arcpy.management.CreateFileGDB(str(gdb.parent), gdb.name)

        base_name = Path(str(input_fc)).stem
        out_path = str(gdb / base_name)
        if arcpy.Exists(out_path):
            raise ValueError(f"Output already exists: {out_path}")
        table_path = str(gdb / (base_name + "_attributes"))
        if join_table is not None and arcpy.Exists(table_path):
            raise ValueError(f"Output already exists: {table_path}")

        arcpy.management.Project(str(input_fc), out_path, out_sr)

        if join_table is not None:
            arcpy.management.CreateTable(str(gdb), base_name + "_attributes")
            arcpy.management.AddField(table_path, join_field, "TEXT", field_length=255)
            arcpy.management.AddField(table_path, value_field, "DOUBLE")

            with open(join_table, "r", newline="", encoding="utf-8-sig") as source:
                reader = csv.DictReader(source)
                with arcpy.da.InsertCursor(table_path, [join_field, value_field]) as cursor:
                    for row in reader:
                        key = row[join_field].strip()
                        value = float(row[value_field])
                        cursor.insertRow((key, value))

            arcpy.management.JoinField(
                out_path, join_field, table_path, join_field, [value_field])

        return out_path

    except arcpy.ExecuteError:
        print("ArcPy tool error:")
        print(arcpy.GetMessages(2))
        raise
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        raise


# Problem 2 (40 points)
def estimatePopulationInZone(source_polygons, population_field, study_zone,
                             output_fc):
    """Similar to the week 10 and 11 notebook exercises, you overlay a buffer with source_polygons 
    such as census units, and calculate the proportion of a source polygon that overlaps 
    with the buffer (the study zone) using areal interpolation. 
    Combine the study zone, intersect, calculate area-weighted population,
    and total the estimates. Save SRC_KM2, PART_KM2, and EST_POP; return the total.
    Inputs must share a projected CRS in meters. 
    """
    pass

    try:
        check_exists(source_polygons, "Source polygons")
        check_exists(study_zone, "Study zone")
        check_shape_type(source_polygons, "Polygon", "Source polygons")
        check_shape_type(study_zone, "Polygon", "Study zone")
        check_fields(source_polygons, [population_field])
        check_field_types(source_polygons, population_field,
                          ["Integer", "SmallInteger", "Double", "Single"])

        # The new fields must not already exist in the source
        existing = [f.name.lower() for f in arcpy.ListFields(str(source_polygons))]
        for new_name in ["SRC_KM2", "PART_KM2", "EST_POP"]:
            if new_name.lower() in existing:
                raise ValueError(f"Source polygons already have a field named {new_name}")

        # Both inputs must be projected in meters and share the same CRS
        crs_source = check_projected_meters(source_polygons)
        crs_zone = check_projected_meters(study_zone)
        if crs_source != crs_zone:
            raise ValueError(f"Coordinate systems differ: {crs_source} vs {crs_zone}")

        check_output_location(output_fc)
        output_fc = str(output_fc)
        gdb = str(Path(output_fc).parent)

        zone_one = arcpy.CreateUniqueName("zone_dissolved", gdb)
        source_copy = arcpy.CreateUniqueName("source_copy", gdb)

        # Dissolve merges overlapping zone polygons so overlap is counted once
        arcpy.management.Dissolve(str(study_zone), zone_one)

        arcpy.management.CopyFeatures(str(source_polygons), source_copy)
        arcpy.management.AddField(source_copy, "SRC_KM2", "DOUBLE")
        arcpy.management.CalculateField(
            source_copy, "SRC_KM2", "!shape.area@squarekilometers!", "PYTHON3")

        arcpy.analysis.Intersect([source_copy, zone_one], output_fc)

        arcpy.management.AddField(output_fc, "PART_KM2", "DOUBLE")
        arcpy.management.CalculateField(
            output_fc, "PART_KM2", "!shape.area@squarekilometers!", "PYTHON3")

        arcpy.management.AddField(output_fc, "EST_POP", "DOUBLE")
        expression = "!" + population_field + "! * !PART_KM2! / !SRC_KM2!"
        arcpy.management.CalculateField(output_fc, "EST_POP", expression, "PYTHON3")

        total = 0.0
        with arcpy.da.SearchCursor(output_fc, ["EST_POP"]) as rows:
            for row in rows:
                if row[0] is not None:
                    total = total + row[0]

        arcpy.management.Delete(zone_one)
        arcpy.management.Delete(source_copy)
        return total

    except arcpy.ExecuteError:
        print("ArcPy tool error:")
        print(arcpy.GetMessages(2))
        raise
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        raise


# Problem 3 (40 points)
def summarizeLineLength(lines, polygons, polygon_id_field, output_fc):
    """Compute the total length of lines that intersect a polygon. 
    Intersect, measure lengths, summarize by polygon ID, and join totals back.
    Save all polygons with LINE_KM (zero if no lines); return output_fc.
    Use a shared projected CRS in meters.
    """
    pass

def summarizeLineLength(lines, polygons, polygon_id_field, output_fc):
    try:
        # Step 1: check the inputs
        check_exists(lines, "Lines")
        check_exists(polygons, "Polygons")
        check_shape_type(lines, "Polyline", "Lines")
        check_shape_type(polygons, "Polygon", "Polygons")
        check_fields(polygons, [polygon_id_field])
        check_field_types(polygons, polygon_id_field,
                          ["String", "Integer", "SmallInteger"])

        existing = [f.name.lower() for f in arcpy.ListFields(str(polygons))]
        if "line_km" in existing:
            raise ValueError("Polygons already have a field named LINE_KM")

        crs_lines = check_projected_meters(lines)
        crs_polygons = check_projected_meters(polygons)
        if crs_lines != crs_polygons:
            raise ValueError(f"Coordinate systems differ: {crs_lines} vs {crs_polygons}")

        ids = []
        with arcpy.da.SearchCursor(str(polygons), [polygon_id_field]) as rows:
            for row in rows:
                ids.append(row[0])
        if None in ids:
            raise ValueError(f"'{polygon_id_field}' has empty values")
        if len(ids) != len(set(ids)):
            raise ValueError(f"'{polygon_id_field}' values are not unique")

        check_output_location(output_fc)
        output_fc = str(output_fc)
        gdb = str(Path(output_fc).parent)

        pieces = arcpy.CreateUniqueName("line_pieces", gdb)
        summary_table = arcpy.CreateUniqueName("line_summary", gdb)

        arcpy.analysis.Intersect([str(polygons), str(lines)], pieces,
                                 join_attributes="ALL", output_type="LINE")
        check_fields(pieces, [polygon_id_field])

        arcpy.management.AddField(pieces, "LINE_KM", "DOUBLE")
        arcpy.management.CalculateField(
            pieces, "LINE_KM", "!shape.length@kilometers!", "PYTHON3")

        arcpy.management.CopyFeatures(str(polygons), output_fc)
        arcpy.management.AddField(output_fc, "LINE_KM", "DOUBLE")
        arcpy.management.CalculateField(output_fc, "LINE_KM", "0", "PYTHON3")

        count = int(arcpy.management.GetCount(pieces)[0])
        if count > 0:
            arcpy.analysis.Statistics(
                pieces, summary_table, [["LINE_KM", "SUM"]], polygon_id_field)
            arcpy.management.JoinField(
                output_fc, polygon_id_field, summary_table, polygon_id_field,
                ["SUM_LINE_KM"])
            arcpy.management.CalculateField(
                output_fc, "LINE_KM",
                "!SUM_LINE_KM! or 0", "PYTHON3")
            arcpy.management.DeleteField(output_fc, "SUM_LINE_KM")
            arcpy.management.Delete(summary_table)

        arcpy.management.Delete(pieces)
        return output_fc

    except arcpy.ExecuteError:
        print("ArcPy tool error:")
        print(arcpy.GetMessages(2))
        raise
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}")
        raise

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == "__main__" and hawkid()[1] == "hawkid":
    print("### Error: YOU MUST provide your HawkID in the hawkid() function.")
