﻿ SELECT url, formats from data where source = 'b' and checked = False and not (SELECT formats   && '{"CSV", "XLS", "XLSX", "JSON", "SHP", "KML", "KMZ", "RDF", "ZIP", "GEOJSON", "GML", "GPX", "GJSON", "TIFF","WMS", "WFS", "GML2", "GML3", "SHAPE", "OVL", "IKT", "CRS", "TCX", "DBF", "SHX"}'::text[])