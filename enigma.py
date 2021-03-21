# import modules
import time
import string
import pandas as pd
import itertools

#functions to read in the notches and rotors from csv
def rotors_read():
    rotor_df = pd.read_csv('rotor_mapping.csv', index_col='Label')
    list_of_rotors = rotor_df.index.tolist()
    rotor_dict = dict(zip(list_of_rotors, rotor_df.to_dict('records')))
    return rotor_dict

def notches_read():
    notches_df = pd.read_csv('notches.csv')
    notches_dict = dict(zip(notches_df['Rotor'].tolist(), notches_df['Notch'].tolist()))
    return notches_dict

# plug leads called by plugboard which is called by Enigma. Uses alphabet dictionaries to map letters
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
        self.__board = dict((letter, letter) for letter in string.ascii_uppercase)
        self.__numleads = 0
        self.__already_wired = []
        self.__leadlimit = 10

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


class Enigma:

    def __init__(self, input='', rotors=[], reflector='A', rings=['01','01','01'], pos='AAZ', plugs=[]):
        self.rotor_dict = rotors_read()
        self.notch_dict = notches_read()
        self.plugs = plugs
        self.board = Plugboard()
        self.string = input.upper()
        self.rotors = [self.rotor_dict[rotor] for rotor in rotors[::-1]]  # read backwards for enigma wiring
        self.rotor_keys = rotors[::-1]                                    # read backwards for enigma wiring
        self.reflector = self.rotor_dict[reflector]
        self.rings = [int(ring) for ring in rings]
        self.pos = list(pos)
        self.output = ''
        self.alpha = list(string.ascii_uppercase)
        self.offset_list_rev = [0] * len(pos)

    # methods used for the 'Single Rotor Demo' in jupyter notebook
    def encode_right_to_left(self,letter):
        return self.rotors[0][letter]

    def encode_left_to_right(self,letter):
        reverse_rotor = {value: key for key, value in self.rotors[0].items()}
        return reverse_rotor[letter]

    # code to run machine
    def run_machine(self, code5=False):
        # in order to change the reflector property of Class for breaking code 5
        if code5:
            self.reflector = code5

        self.plugboard_setup(self.string)
        output_temp = ''
        for letter in self.output:
            self.click()
            output_temp += self.reverse_rotors(self.pass_reflector(self.pass_rotors(letter)))
        self.output = self.plugboard_code(output_temp)
        return self.output

    def plugboard_code(self, letters):
        return ''.join([self.board.encode(letter) for letter in letters])

    def plugboard_setup(self, letters):
        for item in self.plugs:
            self.board.add(PlugLead(item))
        self.output = self.plugboard_code(letters)

    # Recursive function used to determine how many rotors (from left) should turn
    def click_temp(self, counter, ii):
        for key in self.notch_dict.keys():
            if counter <= len(self.pos) - 1:
                if key == self.rotor_keys[ii] and self.pos[-(ii + 1)] == self.notch_dict[key]:
                    counter = self.click_temp(counter + 1, ii + 1)
        return counter

    # Keypress
    def click(self):
        counter = self.click_temp(1, 0)
        for i in range(1, counter + 1):
            #4th rotor doesnt turn
            if i != 4:
                #shift rotors
                self.pos[-i] = self.shift_one(self.pos[-i])

        # Doublestep- checks if 2nd rotor is on notch only when it hasnt been moved by the first notch
        if counter <= 1:
            doublecounter = self.click_temp(1, 1)
            for i in range(2, doublecounter + 1):
                # 4th rotor doesnt turn
                if i != 4:
                    self.pos[-i] = self.shift_one(self.pos[-i])

    # shift rotor one place
    def shift_one(self, position):
        position_offset = ord(position) - ord('A')
        return self.alpha[(position_offset + 1) % len(self.alpha)]

    def pass_rotors(self, letter):
        # pass all rotors
        for ii, rotor in enumerate(self.rotors):
            #account for offset
            letter = rotor[self.offset(ii, letter)]
            # account for offset from ring with original offset (26 characters) same as offset above but with ring added
            letter = self.alpha[
                (26 - self.offset_list_rev[ii] + (self.rings[::-1][ii] - 1) + (ord(letter) - ord('A'))) % len(
                    self.alpha)]
        return letter

    def pass_reflector(self, letter):
        return self.reflector[letter]

    def offset(self, position, string_letter):
        #find total offset
        position_letter = self.pos[::-1][position]
        ring_position = self.rings[::-1][position]
        position_offset = ord(position_letter) - ord('A')
        string_offset = ord(string_letter) - ord('A')
        total_offset = position_offset + string_offset - ring_position + 1
        self.offset_list_rev[position] = position_offset
        return self.alpha[total_offset % len(self.alpha)]

    #pass through rotors as above but in reverse
    def reverse_rotors(self, letter):
        offset_list = self.offset_list_rev[::-1]
        for ii, rotor in enumerate(self.rotors[::-1]):
            reverse_rotor = {value: key for key, value in rotor.items()}
            letter = self.alpha[
                (26 + offset_list[ii] - (self.rings[ii] - 1) + (ord(letter) - ord('A'))) % len(self.alpha)]
            letter = reverse_rotor[letter]
            letter = self.alpha[
                (26 - offset_list[ii] + (self.rings[ii] - 1) + (ord(letter) - ord('A'))) % len(self.alpha)]
        return letter

#
def code_breaker(code_num):
    if code_num == 1:
        crib = 'SECRETS'
        #cycle through reflectors to find the one containing that outputs the crib
        for ref in ['A', 'B', 'C']:
            code1 = Enigma(input='DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ', rotors=['Beta', 'Gamma', 'V'],
                           reflector=ref, plugs=['KI', 'XN', 'FL'], pos='MJM', rings=['04', '02', '14'])
            out = code1.run_machine()
            if crib in out:
                return out, ref

    if code_num == 2:
        crib = 'UNIVERSITY'
        pos_combs = [''.join(i) for i in itertools.product(list(string.ascii_uppercase), repeat=3)]
        # cycle through combinations of initial positions to find the one that outputs the crib
        for initial_positions in pos_combs:
            code2 = Enigma(input='CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH', rotors=['Beta', 'I', 'III']
                           , pos=initial_positions, reflector='B', plugs=['VH', 'PT', 'ZG', 'BJ', 'EY', 'FS'],
                           rings=['23', '02', '10'])
            out = code2.run_machine()
            if crib in out:
                return out, initial_positions

    if code_num == 3:
        crib = 'THOUSANDS'
        #possible ring settings (no odd numbers)
        poss_ring = [i for i in range(1, 27) if not i % 2 and not int(str(i)[::-1]) % 2]
        #cycle through possible ring settings, possible rotors (no odd numbers) and all reflectors
        for rotor in [i for i in itertools.product(['II', 'Gamma', 'IV', 'Beta'], repeat=3)]:
            for ring in [i for i in itertools.product(poss_ring, repeat=3)]:
                for ref in ['C', 'B', 'A']:
                    code3 = Enigma(
                        input='ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY',
                        rotors=rotor,
                        reflector=ref, plugs=['FH', 'TS', 'BE', 'UQ', 'KD', 'AL'], pos='EMY', rings=ring)
                    out = code3.run_machine()
                    if crib in out:
                        return out, rotor, ring, ref

    if code_num == 4:
        crib = 'TUTOR'
        answer_list = []
        #cycle through combinations of possible letters to be paired with A (letter1) and I (letter2)
        for letter1 in [i for i in list(string.ascii_uppercase) if i not in 'AWPRJVFHNCGBSI']:
            for letter2 in [i for i in list(string.ascii_uppercase) if i not in 'AWPRJVFHNCGBSI']:
                if letter1 != letter2:
                    code4 = Enigma(input='SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW',
                                   rotors=['V', 'III', 'IV']
                                   , pos='SWU', reflector='A',
                                   plugs=['WP', 'RJ', 'VF', 'HN', 'CG', 'BS', 'A' + str(letter1), 'I' + str(letter2)],
                                   rings=['24', '12', '10'])
                    out = code4.run_machine()
                    if crib in out:
                        answer_list.append((out, letter1, letter2))
        return answer_list[2]

    if code_num == 5:
        rotor_dictionary = rotors_read()
        #cycle through reflectors
        for R in ['B','A','C']:
            ref_list = []
            unmodified_ref = rotor_dictionary[R]
            dict_list = []
            letters = ''
            # create a list of dictionaries of combinations of 13 letter pairs for each reflector
            for tuple in list(unmodified_ref.items()):
                if tuple[0] not in letters and tuple[1] not in letters:
                    dict_list.append(tuple)
                    letters += (tuple[0] + tuple[1])
            # list of all permutations of 4 pairs of letters out of the 13 choices to then iterate through
            perms = list(itertools.permutations(dict_list, 4))

            for pairs in perms:
                # iterate through the 3 ways of representing each of the 4 pairs that arent the original
                for jj in range(1, 4):
                    unmodified_ref = rotor_dictionary[R].copy()
                    # create a new dictionary for the 3 ways, and append to a list
                    for ii in range(len(pairs)):
                        swap_pairs = [(pairs[(ii) % len(pairs)][0], pairs[(ii + jj) % len(pairs)][1])]
                        for element in swap_pairs:
                            del unmodified_ref[element[0]]
                            del unmodified_ref[element[1]]
                            new_pair = {element[0]: element[1], element[1]: element[0]}
                            unmodified_ref.update(new_pair)
                        ref_list.append(unmodified_ref)

            # cycle through the list of new dictionaries of all possible letter mappings
            for ref in ref_list:
                code5 = Enigma(input='HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX', rotors=['V', 'II', 'IV']
                               , pos='AJL', reflector='A', plugs=['UG', 'IE', 'PO', 'NX', 'WT'],
                               rings=['06', '18', '07'])
                out = code5.run_machine(code5=ref)
                #iterate through list of social media brands
                for crib in ['FACEBOOK','TWITTER','INSTAGRAM','LINKEDIN','YOUTUBE','PINTEREST','TUMBLR','FLICKER','REDDIT',
                             'SNAPCHAT','WHATSAPP']:
                    if crib in out:
                        #show which pairs were modified
                        original_pairs = list(set(list(rotor_dictionary[R].items())) - set(list(ref.items())))
                        changed_pairs = list(set(list(ref.items())) - set(list(rotor_dictionary[R].items())))
                        return out, crib, R, 'original pairs:', original_pairs, 'changed pairs', changed_pairs









if __name__ == "__main__":
    # instance = Enigma(input='HELLOWORLD', rotors=['I', 'II', 'III'], reflector='B', plugs=['HL','MO','AJ','CX','BZ','SR','NI','YW','DG','PK'], pos='AAZ', rings=['01', '01', '01'])
    # instance.run_machine()
    #
    # instance = Enigma(input='RFKTMBXVVW', rotors=['I', 'II', 'III'], reflector='B', plugs=['HL','MO','AJ','CX','BZ','SR','NI','YW','DG','PK'], pos='AAZ', rings=['01', '01', '01'])
    # instance.run_machine()

    # instance = Enigma(input='BUPXWJCDPFASXBDHLBBIBSRNWCSZXQOLBNXYAXVHOGCUUIBCVMPUZYUUKHI', rotors=['IV', 'V', 'Beta','I'], reflector='A', plugs=['PC','XZ','FM','QA','ST','NB','HY','OR','EV','IU'], pos='EZGP', rings=['18', '24', '03','05'])
    # instance = instance.run_machine()
    #
    # instance2 = Enigma(input=instance, rotors=['IV', 'V', 'Beta','I'], reflector='A', plugs=['PC','XZ','FM','QA','ST','NB','HY','OR','EV','IU'], pos='EZGP', rings=['18', '24', '03','05'])
    # print(instance2.run_machine())


    # testing code to break all codes and calculate timing using time lib
    def break_all_codes():
        tic = time.perf_counter()
        for i in range(1,6):
            print(code_breaker(i))
            toc = time.perf_counter()
            print(f"{toc - tic:0.4f} seconds")

    break_all_codes()



