import string
import pandas as pd
from googletrans import Translator

"""
The code below is the same as enigma.py so look there for comments on functionality.
This code will highlight mods used for the advanced work with a #AW as well as explain the new functionality
In the advanced work there is 2 characters added to the dictionaries of rotors and reflectors and initial positions
These are " " and "."
" " is modified to "_" in the code to better keep track, before being modified back to " " before outputting

A google translate API is then utilised to translate decrypted strings
"""


# READS IN MODIFIED ROTOR LISTS
def rotors_read():
    rotor_df = pd.read_csv('rotor_mapping_ext.csv', index_col='Label')
    list_of_rotors = rotor_df.index.tolist()
    rotor_dict = dict(zip(list_of_rotors, rotor_df.to_dict('records')))
    return rotor_dict


def notches_read():
    notches_df = pd.read_csv('notches.csv')
    notches_dict = dict(zip(notches_df['Rotor'].tolist(), notches_df['Notch'].tolist()))
    return notches_dict


class PlugLead:
    def __init__(self, mapping):
        self.lead = mapping.upper()
        self.ends = {self.lead[0]: self.lead[1], self.lead[1]: self.lead[0]}

    def encode(self, character):
        if character in self.ends.values():
            return self.ends[character]
        return character


class Plugboard:

    def __init__(self):
        # AW - added characters
        self.__board = dict(dict((letter, letter) for letter in string.ascii_uppercase),**{'_' : '_' , '.' :'.'})
        self.__numleads = 0
        self.__already_wired = []
        # AW - Modified for optimal max (see advanced work in jupyter notebook)
        self.__leadlimit = 12

    def add(self, wire):
        wire_letters = list(wire.lead)
        already_filled = list(set(wire_letters).intersection(self.__already_wired))
        if len(already_filled) > 0:
            print(f"Sorry, letter(s) {','.join(already_filled)} already filled.")

        elif self.__numleads > self.__leadlimit:
            print(f"Sorry, max number of leads realised.")
        # replace keys in dictionary with new ones
        else:
            del self.__board[wire.lead[0]]
            del self.__board[wire.lead[1]]
            self.__board.update(wire.ends)
            self.__already_wired.extend(wire_letters)
            self.__numleads += 1

    def encode(self, character):
        return self.__board[character]


class Advanced_Enigma:

    def __init__(self, input='', rotors=[], reflector='A', rings=[], pos='', plugs=[]):
        self.rotor_dict = rotors_read()
        self.notch_dict = notches_read()
        self.plugs = plugs
        self.board = Plugboard()
        #AW - space replaces with '_'
        self.string = input.replace(" ", "_").upper()
        self.rotors = [self.rotor_dict[rotor] for rotor in rotors[::-1]]
        self.rotor_keys = rotors[::-1]
        self.reflector = self.rotor_dict[reflector]
        self.rings = [int(ring) for ring in rings]
        self.pos = list(pos)
        self.output = ''
        #AW - Characters added
        self.alpha = list(string.ascii_uppercase)+['_','.']
        self.offset_list_rev = [0] * len(pos)



    def run_machine(self, code5=False):
        if code5:
            self.reflector = code5
        self.plugboard_setup(self.string)
        output_temp = ''
        for letter in self.output:
            self.click()
            output_temp += self.reverse_rotors(self.pass_reflector(self.pass_rotors(letter)))
        self.output = self.plugboard_code(output_temp)
        #AW - Characters added
        self.output = self.output.replace("_", " ")
        return self.output

    def plugboard_code(self, letters):
        return ''.join([self.board.encode(letter) for letter in letters])

    def plugboard_setup(self, letters, reverse=False):
        for item in self.plugs:
            self.board.add(PlugLead(item))
        self.output = self.plugboard_code(letters)

    def click_temp(self, counter, ii):
        for key in self.notch_dict.keys():
            if counter <= len(self.pos) - 1:
                if key == self.rotor_keys[ii] and self.pos[-(ii + 1)] == self.notch_dict[key]:
                    counter = self.click_temp(counter + 1, ii + 1)
        return counter

    def click(self):
        counter = self.click_temp(1, 0)
        for i in range(1, counter + 1):
            #4th rotor doesnt turn
            if i != 4:
                self.pos[-i] = self.shift_one(self.pos[-i])

        #doublestep
        doublecounter = self.click_temp(1, 1)
        if counter <= 1:
            for i in range(2, doublecounter + 1):
                # 4th rotor doesnt turn
                if i != 4:
                    self.pos[-i] = self.shift_one(self.pos[-i])

    def shift_one(self, position):
        # AW - ord of added characters not in correct order so corrected
        position_offset = ord(position) - ord('A')
        if position == '_':
            position_offset = 26
        if position == '.':
            position_offset = 27
        return self.alpha[(position_offset + 1) % len(self.alpha)]

    def pass_rotors(self, letter):
        for ii, rotor in enumerate(self.rotors):
            letter = rotor[self.offset(ii, letter)]
            letter_diff = ord(letter) - ord('A')
            # AW - ord of added characters not in correct order so corrected
            if letter == '_':
                letter_diff = 26
            if letter == '.':
                letter_diff = 27
            letter = self.alpha[
                (28 - self.offset_list_rev[ii] + (self.rings[::-1][ii] - 1) + letter_diff) % len(
                    self.alpha)]
        return letter

    def pass_reflector(self, letter):
        letter = self.reflector[letter]
        return letter

    def offset(self, position, string_letter):
        position_letter = self.pos[::-1][position]
        ring_position = self.rings[::-1][position]
        position_offset = ord(position_letter) - ord('A')
        string_offset = ord(string_letter) - ord('A')
        # AW - ord of added characters not in correct order so corrected
        if position_letter == '_':
            position_offset = 26
        if position_letter == '.':
            position_offset = 27
        if string_letter == '_':
            string_offset = 26
        if string_letter == '.':
            string_offset = 27
        total_offset = position_offset + string_offset - ring_position + 1
        self.offset_list_rev[position] = position_offset
        return self.alpha[total_offset % len(self.alpha)]

    def reverse_rotors(self, letter):
        offset_list = self.offset_list_rev[::-1]
        for ii, rotor in enumerate(self.rotors[::-1]):
            reverse_rotor = {value: key for key, value in rotor.items()}
            letter_diff = ord(letter) - ord('A')
            # AW - ord of added characters not in correct order so corrected
            if letter == '_':
                letter_diff = 26
            if letter == '.':
                letter_diff = 27

            letter_temp = self.alpha[
                (28 + offset_list[ii] - (self.rings[ii] - 1) + letter_diff) % len(self.alpha)]

            letter = reverse_rotor[letter_temp]
            letter_diff = ord(letter) - ord('A')
            # AW - ord of added characters not in correct order so corrected
            if letter == '_':
                letter_diff = 26
            if letter == '.':
                letter_diff = 27

            letter = self.alpha[
                (28 - offset_list[ii] + (self.rings[ii] - 1) + letter_diff) % len(self.alpha)]
        return letter

    # This could probably be a static method, but it's left as is to keep consistent
    def translate_and_decrypt(self,language_in, language_out):
        translator = Translator()
        return translator.translate(self.run_machine(), src = language_in, dest=language_out).text



#Tests
if __name__ == "__main__":
    instance = Advanced_Enigma(input='HELLO WORLD. THIS IS A TEST.', rotors=['I', 'II', 'III'], reflector='B', plugs=[], pos='AA.', rings=['01', '01', '01'])

    instance2 = Advanced_Enigma(input=instance.run_machine(), rotors=['I', 'II', 'III'], reflector='B', plugs=[], pos='AA.', rings=['01', '01', '01'])
    translator = Translator()
    print(translator.translate(instance2.run_machine(),src = 'en',dest='de').text)
