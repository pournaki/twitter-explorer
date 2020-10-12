def iso_to_string(isostring):
    split = isostring.split("T")
    datetimestring = split[0] + " " + split[1][:5]
    return datetimestring