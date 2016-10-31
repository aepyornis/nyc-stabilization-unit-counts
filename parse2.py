#!/user/bin/env python3

'''
Updated script to convert property tax PDFS.
'''
import re
import argparse
# import sys
# filepath = sys.argv[1]
filepath = "/home/zy/code/nyc-stabilization-unit-counts/data/1/01629/0062/August 21, 2015 - Quarterly Property Tax Bill.txt"

tax_bill = {}

def g_or_n(match):
    """calls .group(1) on match object or returns None"""
    return match.group(1) if match is not None else None

def strip_or_n(s):
    """str.strip with type check. return str or None """
    if isinstance(s, str):
        return s.strip()
    else:
        return None

def is_blank(line):
    ''' str -> boolean  '''
    return len(line.strip()) == 0

def set_value(prop, value, d = tax_bill):
    """Sets the propery (prop) on the dictionary (d)"""
    d[prop] = value


def set_prop_if(prop, func, line):
    '''  str, func, str -> boolean
    Sets provided property on the tax_bill dictionary to be the
    result of func(line)  and return true.
    If result is none, then it returns false without setting any property.
    '''
    result = func(line)
    if result:
        set_value(prop, result)
        return True
    else:
        return False


def line_search(prop, func):
    ''' string, func -> func '''
    return lambda line: set_prop_if(prop, func, line)


## Line testers
## These either return false or the val of the property as a string
## These are are properties that can be found on one line
###################################################################

def activity_through(line):
    return g_or_n(re.compile('Activity through (.*)', re.I).match(line))


def owner_name(line):
    line = line.split("    ")[0].strip()
    return g_or_n(re.compile('owner name[:]?[ ]?(.*)', re.I).match(line))


def property_address(line):
    line = line.split("    ")[0].strip()
    return g_or_n(re.compile('property address[:]?[ ]?(.*)', re.I).match(line))


def boro_block_lot(line):
    line = line.split("    ")[0].strip()
    return g_or_n(re.compile('Borough,? block [&]? lot:?[ ]?(.*)', re.I).match(line))


def previous_charges(line):
    if "due date" in line.lower():
        # this skips the line that contains the phrase 'previous charges' but not the actual data
        return None
    else:
        return strip_or_n(g_or_n(re.compile('previous charges:?(.*)', re.I).match(line)))


def amount_paid(line):
    return strip_or_n(g_or_n(re.compile('amount paid:?(.*)', re.I).match(line)))


def interest(line):
    if "previous charges" in line.lower() or "payments" in line.lower():
        return None
    else:
        return strip_or_n(g_or_n(re.compile('interest:?(.*)', re.I).match(line)))

def unpaid_charges(line):
    return strip_or_n(g_or_n(re.compile('Unpaid charges, if any(.*)', re.I).match(line)))


TESTERS = [
    ('activity_through', activity_through),
    ('owner_name', owner_name),
    ('property_address', property_address),
    ('bbl', boro_block_lot),
    ('previous_charges', previous_charges),
    ('amount_paid', amount_paid),
    ('interet', interest),
    ('unpaid_charges', unpaid_charges)
]


def single_line_props(filepath):
    with open(filepath, 'r') as doc:
        for line in doc:  # loop through all lines in document
            line = line.strip()
            if is_blank(line):
                continue # skip line if blank

            for prop, func in TESTERS:
                # try each of the testers defined above
                if line_search(prop, func)(line):
                    break   # stop if a propety is found

#
# Multi-line search
# These all take the entire doc (file.readliens())

def mailing_address(lines):
    """
    Here is a example of lines that this fuction is trying to parse:
    
                                                                                 Mailing address:
       Owner name: 530 CANAL ST. REALTY CORP.                                    530 CANAL ST. REALTY CORP.
       Property address: 530 CANAL ST.                                           271 MADISON AVE. STE 1101
       Borough, block & lot: MANHATTAN (1), 00595, 0011                          NEW YORK , NY 10016-1001

    """
    address_accumulator = []
    line_reader = iter(lines)
    rm_eol_strip = lambda line: line.replace('\n', '').strip()
    for line in line_reader:
        if "mailing address" in line.lower():
            # nested loop on same iterable ... bad idea? ... oh well ...
            for address_part in line_reader:
                ll = address_part.lower()
                if 'owner name' in ll or 'property address' in ll or 'borough' in ll:
                    address_accumulator.append(rm_eol_strip(address_part).split('     ')[-1].strip())
                elif len(address_part.replace('\n', '').strip()) > 0:
                    address_accumulator.append(rm_eol_strip(address_part))
                else:
                    return "\n".join(address_accumulator)


def multiple_line_props(filepath):
    with open(filepath, 'r') as doc:
        lines = doc.readlines()
        set_value('mailing_address', mailing_address(lines))

def main():
    single_line_props(filepath)
    multiple_line_props(filepath)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Parse tax bills')
    main()
    print(tax_bill)



