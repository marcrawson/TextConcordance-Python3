import fileinput
import sys
import re

# file_info (tuple) index constants:
EXCL_WORDS  = 0
INDEX_LINES = 1
KEYWORDS    = 2

# line_key_pair (tuple) index constants:
LINE  = 0
KEY   = 1
INDEX = 2

# output specification [index] constants:
FIRST_POSSIBLE_SPACE   = 8
MAX_LEN_BEFORE_KEYWORD = 19
KEYWORD_INDEX          = 29
MAX_LEN_AFTER_KEYWORD  = 31
LAST_POSSIBLE_SPACE    = 60

class concord:
    def __init__(self, input=None, output=None):
        '''
        __init__ constructs object containing input and output.
        If an output is given, the output of full_concordance is
        written line-by-line to the specified file.
        '''
        self.input = input
        self.output = output
        if self.output != None:
            self.__writeFile()

    def __writeFile(self):
        '''
        __writeFile calculates output of full_concordance,
        the specified output file is then opned written to line-by-line,
        then the file is closed.
        '''
        concord_output = self.full_concordance()
        f = open(self.output, "w")
        for line in concord_output:
            line = line + "\n"
            f.write(line)
        f.close

    def __loadInput(self):
        '''
        __loadInput reads from specified input file (if provided),
        otherwise reads from stdin. Then __loadInput interprets format and
        generates a list of exclusion words (excl_words) and
        index lines (index_lines). The file input is completely read,
        excl_words and input_lines are added to a tuple (file_info)
        '''
        excl_words = []
        index_lines = []
        done_excl = False
        file_info = ()

        for line in fileinput.input(files = self.input):
            line = line.strip()
            if line == "2":
                continue
            elif line == "\'\'\'\'":
                continue
            elif line == "\"\"\"\"":
                done_excl = True
                continue
            elif line == "":
                continue

            if done_excl:
                index_lines.append(line)
            else:
                excl_words.append(line.lower())

        file_info = (excl_words, index_lines)
        return file_info

    def __findKeywords(self, file_info):
        '''
        __findKeywords takes argument file_info as a tuple of exclusion words
        and index lines. __findKeywords finds all words appearing in index
        lines that do not appear in exclusion words and adds them to a list
        (keywords). keywords is lexicographically sorted and added to
        file_info (tuple) and file_info is returned.
        '''
        keywords = []
        for line in file_info[INDEX_LINES]:
            words = re.split(r" ", line)
            for word in words:
                lower_word = word.lower()
                if lower_word not in file_info[EXCL_WORDS]:
                    keywords.append(lower_word)
        keywords.sort()
        file_info += (keywords,)
        return file_info

    def __buildOutput(self, file_info):
        '''
        __buildOutput takes file_info (tuple) as an argument and iterates
        through keywords and index lines, determining if the current keyword is
        found in the current index line. If yes, then the keyword is replaced
        by the fully capitalized version of the keyword. The starting index
        of the keyword is stored and the output string, uppercase keyword,
        and index are stored in line_key_pair (tuple). line_key_pair
        is unique to each keyword and each is added to output_lines (list)
        andoutput_lines is returned.
        '''
        output_lines = []
        for keyword in file_info[KEYWORDS]:
            line_key_pair = ()
            temp_keyword = keyword.rstrip("\n")
            for line in file_info[INDEX_LINES]:
                temp_line = line.rstrip("\n")
                re_str = r"\b" + temp_keyword + r"\b"
                matchobj = re.search(re_str, temp_line, flags=re.IGNORECASE)
                if matchobj:
                    key = keyword.upper()
                    output = re.sub(re_str, key, line, flags=re.IGNORECASE)
                    if output not in output_lines:
                        idx = matchobj.start()
                        line_key_pair = (output, keyword.upper(), idx)
                        output_lines.append(line_key_pair)
        return output_lines

    def __formatOutput(self, output_lines):
        '''
        __formatOutput takes output_lines [list(tuple)] and returns a formatted
        version of each line found in output_lines according to a4
        specifications.
        '''
        formatted_output = []
        for line_key in output_lines:
            line = line_key[LINE]
            key = line_key[KEY]
            key_index = line_key[INDEX]
            before_key = KEYWORD_INDEX - key_index

            # aligns keywords to the 30th column
            if before_key > 0:
                buffer = " " * before_key + line
            elif before_key == 0:
                buffer = line
            else:
                abs_before_key = abs(before_key)
                buffer = re.sub(r'.', '', line, count = abs_before_key)
            
            # if length before keyword is > 20: then find first space after 8th column
            if key_index > MAX_LEN_BEFORE_KEYWORD:
                space_idxs = [(m.start(0)) for m in re.finditer(" ", buffer)]
                for idx in space_idxs:
                    if idx >= 8:
                        break
                buffer = re.sub(r'.', ' ', buffer, count = idx)
                
            # if length after and including keyword > 30: then find last space before 61 columnm
            length = len(buffer)
            if (length > LAST_POSSIBLE_SPACE):
                space_idxs = [(m.start(0)) for m in re.finditer(" ", buffer)]
                for idx in space_idxs:
                    if idx <= LAST_POSSIBLE_SPACE:
                        last_space = idx
                buffer = buffer[:last_space]
            if buffer not in formatted_output:
                formatted_output.append(buffer)

        return formatted_output

    def full_concordance(self):
        '''
        full_concordance reads input (from stdin or file depending on
        provided input) and builds a formatted output according to a4
        specifications. Each final output line is stored in an array,
        and then returned.
        '''
        file_info = self.__loadInput()
        file_info = self.__findKeywords(file_info)
        output_lines = self.__buildOutput(file_info)
        formatted_output = self.__formatOutput(output_lines)

        return formatted_output
