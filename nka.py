# Hlboká kópia jedného stavu
def deepcopy_state(original_state, copied_states=None):
    if copied_states is None:
        copied_states = {}

    if original_state in copied_states:
        return copied_states[original_state]
    
    # Nový stav
    state_copy = State(original_state.accept)
    copied_states[original_state] = state_copy  
    
    # Kopíruj prechody, rekurzívne
    for symbol, states in original_state.transitions.items():
        for state in states:
            state_copy.add_transition(symbol, deepcopy_state(state, copied_states))
    
    return state_copy

# Stav v automate
# id - voliteľné
# akceptačný switch
# množina prechodov
class State:
    id_counter = 0

    def __init__(self, accept=False):
        self.id = State.id_counter
        State.id_counter += 1
        self.accept = accept
        self.transitions = {}  # Klúč: symbol, Hodnota: množina stavov

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(state)

    # Reprezentácia objektu vo forme reťazca
    def __repr__(self):
        transitions_repr = {symbol: [s.id for s in states] for symbol, states in self.transitions.items()}
        return f"State({self.id}, Accept={self.accept}, Transitions={transitions_repr})"
    
    def epsilon_closure(self):
        closure = {self}
        stack = [self]
        while stack:
            state = stack.pop()
            for next_state in state.transitions.get('ε', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
            if len(stack) > 100:
                print("Naozaj takéto dlhé?")
                break
        return closure

class NKA:
    def __init__(self):
        self.states = []
        self.start_state = None
        self.accept_states = set()

    def add_state(self, state):
        self.states.append(state)
        if state.accept:
            self.accept_states.add(state)

    def set_start_state(self, state):
        self.start_state = state

    def add_transition(self, from_state, symbol, to_state):
        from_state.add_transition(symbol, to_state)

    def update_accept_states(self):
        self.accept_states = {state for state in self.states if state.accept}

    def simulate(self, input_string):
        current_states = self.start_state.epsilon_closure()
        
        for char in input_string:
            next_states = set()
            for state in current_states:
                # Posunutie do ďalšieho stavu podľa nasledujúceho znaku
                for next_state in state.transitions.get(char, []):
                    next_states |= next_state.epsilon_closure()
            current_states = next_states
        
        # Sleduj, či je akýkoľvek s možných stavov medzi akceptačnými
        return any(state.accept for state in current_states)

    # Reprezentácia objektu vo forme reťazca
    def __repr__(self):
        states_repr = [repr(state) for state in self.states]
        start_state_id = self.start_state.id if self.start_state else 'None'
        accept_states_ids = [state.id for state in self.accept_states]
        return f"NKA(Start={start_state_id}, AcceptStates={accept_states_ids}, States={states_repr})"
    
    # Implementácia hlbokej kópie
    def deepcopy(self):
        copied_states = {}
        new_nka = NKA()
        
        # V cykle vytvor nové stavy
        for state in self.states:
            deepcopy_state(state, copied_states)
        
        for state_copy in copied_states.values():
            new_nka.add_state(state_copy)
        
        # Nastav počiatočný a akceptačné stavy v novom NKA
        if self.start_state is not None:
            new_nka.start_state = copied_states[self.start_state]
        new_nka.accept_states = {copied_states[state] for state in self.accept_states}
        
        return new_nka
