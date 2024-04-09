import sys
from nka import NKA, State

def read_input_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Problém: Súbor '{filename}' nebolo možné otvoriť.")
        sys.exit(1)

# Vytvor hlbokú kópia NKA
def deepcopy_nkas(atomic_nka, *indices):
    copied_nkas = []
    for index in indices:
        try:
            copied_nkas.append(atomic_nka[index].deepcopy())
        except KeyError:
            print(f"Nenašla sa atomická NKA pre riadok {index}")
            sys.exit(1)
    if len(copied_nkas) == 1:
        return copied_nkas[0]
    else:
        return copied_nkas

def process_input(input_data):
    # Pre každý riadok sa tvorí nové NKA, uloží sa do atomic_nka s indexom riadka
    atomic_nka = {} 

    for index, item in enumerate(input_data, start=1):  
        nka = NKA()
        item = item.strip()

        if item == '':
            new_start_state = State(True)
            nka.add_state(new_start_state)

            if nka.start_state is None:
                nka.set_start_state(new_start_state)
                
        elif ',' not in item:
            new_start_state = State()
            new_end_state = State(True)
            new_start_state.add_transition(item, new_end_state)
            
            nka.add_state(new_start_state)
            nka.add_state(new_end_state)

            if nka.start_state is None:
                nka.set_start_state(new_start_state)

        else:
            operation, *operands = item.split(',')
            if operation == 'C':
                i, j = map(int, operands)  
                nfa_1, nfa_2 = deepcopy_nkas(atomic_nka, i, j)

                for end_state_i in nfa_1.accept_states:
                    end_state_i.add_transition('ε', nfa_2.start_state)
                    end_state_i.accept = False  
                nka.set_start_state(nfa_1.start_state)

                for state in nfa_1.states + nfa_2.states:
                    nka.add_state(state)
            
            elif operation == 'U':
                i, j = map(int, operands)  
                nfa_1, nfa_2 = deepcopy_nkas(atomic_nka, i, j)

                new_start_state = State()
                new_start_state.add_transition('ε', nfa_1.start_state)
                new_start_state.add_transition('ε', nfa_2.start_state)
                nka.add_state(new_start_state)
                nka.set_start_state(new_start_state)

                for state in nfa_1.states + nfa_2.states:
                    nka.add_state(state)

            elif operation == 'I':
                i = int(operands[0])  
                nfa_1 = deepcopy_nkas(atomic_nka, i)

                new_start_state = State(True)
                new_start_state.add_transition('ε', nfa_1.start_state)
                nka.add_state(new_start_state)
                nka.set_start_state(new_start_state)

                for end_state_i in nfa_1.accept_states:
                    end_state_i.add_transition('ε', new_start_state)

                for state in nfa_1.states:
                    nka.add_state(state)

            # Synchronizácia akceptačných stavov so súčasnými objektmi
            nka.update_accept_states()
        atomic_nka[index] = nka

    return nka

def main(regex_f, string_f):
    regex_lines = read_input_file(regex_f)
    strings_lines = read_input_file(string_f)[1:]

    nfa = process_input(regex_lines)

    max_word_length = max(len(word.strip()) for word in strings_lines) + 10

    # Spusti NKA pre každé slovo
    for word in strings_lines:
        word = word.strip()
        belongs = "ÁNO" if nfa.simulate(word) else "NIE"
        padded_word = word.ljust(max_word_length)
        print(f"Reťazec {padded_word} Patrí do jazyka z regexu: {belongs}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Použitie: regex.py <regex_file> <string_file>")
        sys.exit(1)
    regex_file = sys.argv[1]
    string_file = sys.argv[2]
    main(regex_file, string_file)
