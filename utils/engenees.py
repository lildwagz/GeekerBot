import os


def initdata(pathprefix=""):
    """Sets up a list of conversion factors that can be read more easily by python. This function contains no code for converting units,
       but converts text files (credit to Fchart Software) to list/string format so as to prevent a different script from doing this multiple times."""

    # defines weeder() locally to make copy-pasting f'n easier
    def weeder(mess):
        goodlist = []
        for item in mess:
            # print('found:',type(item))
            if type(item) == list and item != []:
                # print('recursing')
                goodlist.append(weeder(item))
            elif item != '':
                try:
                    final_item = float(item)
                except:
                    final_item = item
                goodlist.append(final_item)
        return goodlist

    # definition of unit conversion sheet-reader part of the function
    def unitsort():
        # first block of code deals with the text file as a single string
        with open(pathprefix + "units.txt", mode="r", encoding="cp1252") as file:
            # remove indentations
            data = file.read()
        data = data.replace('\n', '?')
        # remove other pesky characters
        data = data.replace('{', '')
        data = data.replace('}', '')
        # remove useless dialog
        data = data.replace(
            '?This file provides definitions of units in terms of a basic set of dimensions.  The basic?dimensions '
            'and the selected unit for each dimension are:??L       length    m?M       Mass    kg?N       Moles   '
            'kmole?T       Time    sec?D       Temperature Difference  K?A       Angle     radian?C       Charge  '
            'coulomb?I       Illuminance lm??You may enter additional unit definitions to this file.  To do so, '
            'enter the unit name followed?by its conversion factor into the selected set of dimenions indicated above '
            'separated with?one or more spaces.  Designate a new dimension type by preceding the description with a '
            '$?and provide the basic dimensions in parentheses.??',
            '')
        # create chunks of units, only items from same chunks may be converted (i.e. Pa cannot convert to K)
        chunks = data.split('$')

        # second block of code deals with the text file as a list of lists of lists...
        # separate units from chunk header
        for chunk in chunks:
            chunks[chunks.index(chunk)] = chunk.split(')')
        # remove first entry (list containing only ' ')
        chunks = chunks[1:len(chunks)]

        # create new, refined list of headers with a list of strings
        goodchunks = []
        for chunk in chunks:
            # try/except prevents crashing on garbage entries
            try:
                goodchunks.append([chunk[0].upper(), chunk[1].split('?')])
            except:
                pass
        betterchunks = []
        # splits up the unit str and its conversion factor
        for chunk in goodchunks:
            bits = []
            for unit in chunk[1]:
                bits.append(unit.split(' '))
            betterchunks.append([chunk[0], bits])  # chunk[0], <- include in the list in .append() to include headers
        # calls weeder function to remove all instances of ''
        final = weeder(betterchunks)

        # makes all conversion data a dict under chunk header as key
        for item in final:
            try:
                convo_factors = item[1]
                convo_dict = {}
                for unit in convo_factors:
                    # print(unit)
                    try:
                        convo_dict[unit[0]] = unit[1]
                    except:
                        # print('not valid dict entry')
                        pass
                item[1] = convo_dict
            except:
                # print('invalid chunk')
                pass
        return final

    # definition of constants data sheet-reader part of the function
    def constantsort():
        # start gathering constants data
        with open(pathprefix + 'constants.txt', 'r') as file:
            # remove indentations
            cdata = file.read().split("\n")

        # split each constant's data into a dict
        nuitem = []
        for item in cdata:
            try:
                nuitem.append({item.split("#")[0]: item.split("\t")[1:]})
            except:
                pass

        final = {}
        for item in nuitem:
            final.update(item)

        return final

    return [unitsort(), constantsort()]


def convert(dataset, fro, to, value=1):
    global denominator
    for item in dataset:
        # if fro in item[1] or to in item[1]:
        # print(item[1])
        try:
            if fro in item[1] and to in item[1]:
                denominator = item[1][fro]
                numerator = item[1][to]
                break
        except:
            pass
    return float((denominator / numerator) * value)


def units_of(dataset, unit):
    UNIT = unit.upper()
    for item in dataset:
        if UNIT in item[0]:
            return '  '.join(item[1])
    return "no units of that type were found"
