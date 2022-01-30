import UnityEngine

# battlegrounds.py
from lib2to3.pgen2 import token
from os import abort, stat
import typing
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
from azure.quantum.qiskit import AzureQuantumProvider
from numpy.random import choice


# game logic
# 1. pool of gates
# 2. build phase
# 3. 

SINGLE_QUBIT_GATES = ['I', 'X', 'Y', 'Z', 'H', 'S']
TWO_QUBIT_GATES = ['CX']
def gate_translate(index):
  if index == 0: return "X"
  if index == 1: return "H"
  if index == 2: return "S"
  if index == 3: return "CX"
  if index == 4: return "I"
  return "BYE";


def pos_translate(index):
  if index < 2:
    return [index]
  
  elif index == 2:
    return [0 ,1]
  else:
    return [1, 0]


def applySQG(circuit, gatename, targets):
    if gatename == 'X':
        circuit.x(targets[0])
    elif gatename == 'Y':
        circuit.y(targets[0])
    elif gatename == 'Z':
        circuit.z(targets[0])
    elif gatename == 'H':
        circuit.h(targets[0])
    elif gatename == 'I':
        circuit.i(targets[0])
    elif gatename == 'S':
        circuit.s(targets[0])
    else:
        print("gate translation not implemented")
        return None

def applyTQG(circuit, gatename, targets):
    if gatename == 'CX':
        circuit.cx(targets[0], targets[1])
    else:
        print("gate translation not implemented")
        return None

def sum_score(bitstring):
        return sum([b=='1' for b in bitstring])

def pick_from_probabilities(probdict:dict):
    val , prob = list(probdict.keys()), list(probdict.values())
    print(val, prob)
    return choice(val, p=prob)

class Player:
    id = None
    minions = {}
    health = 1
    circuit:QuantumCircuit = None

    def __init__(self, id, gate_types):
        self.id = id
        self.minions = gate_types.copy()

    def __str__(self):
        return f"Player {self.id}, health = {self.health}, with minions {self.minions}"



class Arena:
    players = []
    players_remaining = 0
    pool = {}
    hero_pool = {}
    round = 0
    lanes = 0
    shopsize = 5
    current_shop = None

    target_backend = 'ionq.simulator'
    provider = None


    def __init__(self, playercount, lanes, starting_pool, hero_pool, backend=None):
        starting_gates = starting_pool.copy()
        for gate in starting_gates.keys():
            starting_gates[gate] = 0
        self.players = [Player(i+1, starting_gates.copy()) for i in range(playercount)]
        self.players_remaining = playercount
        self.pool = starting_pool
        self.lanes = lanes
        if (not backend==None):
            self.set_backend(backend)

        self.provider = AzureQuantumProvider (
            resource_id = "/subscriptions/b1d7f7f8-743f-458e-b3a0-3e09734d716d/resourceGroups/aq-hackathons/providers/Microsoft.Quantum/Workspaces/aq-hackathon-01",
            location = "eastus"
        )

    def set_backend(self, backend):
        self.target_backend = backend
    
    """
    Hero pick phase
    """


    """
    Buy/sell phase
    """
    def randomize_shop(self):
        gates, amt = list(self.pool.keys()), list(self.pool.values())
        tot = sum(amt)
        probs = list(map(lambda x:x/tot, amt))
        # print(probs)
        self.current_shop = choice(gates, size=self.shopsize, p=probs, replace=False)
        return True
        
    # pid is the id of the player
    # minion is the string name of the gate
    def buy_minion(self, pid, minion):
        if self.pool[minion] <= 0:
            return False

        self.players[pid].minions[minion] += 1
        self.pool[minion] -= 1
        return True

    def sell_minion(self, pid, minion):
        self.players[pid].minions[minion] -= 1
        self.pool[minion] += 1
        return True
    
    """
    Build phase
    """
    # requirement: circuit_data is an array containing pairs (gate, [list of qubits])
    def build_circuit(self, pid, circuit_data):
        circuit = QuantumCircuit(self.lanes, self.lanes)
        for gate_spec in circuit_data:
            if gate_spec[0] in SINGLE_QUBIT_GATES:
                applySQG(circuit, gate_spec[0], gate_spec[1])
            else:
                applyTQG(circuit, gate_spec[0], gate_spec[1])
        self.players[pid].circuit = circuit
    
    """
    Battle phase
    """
    def battle(self, pid1, pid2):
        atob, btoa = self.players[pid1].circuit.copy(), self.players[pid2].circuit.copy()
        atob.barrier()
        btoa.barrier()
        atob, btoa = atob.combine(self.players[pid2].circuit), btoa.combine(self.players[pid1].circuit)
        atob.barrier()
        btoa.barrier()
        atob.measure(range(self.lanes), range(self.lanes))
        btoa.measure(range(self.lanes), range(self.lanes))
        atob.name = f"atob{self.round}"
        btoa.name = f"btoa{self.round}"
        UnityEngine.Debug.Log(f"Round between Player {pid1+1} and Player {pid2+1}")
        # print(atob)
        # print(btoa)

        simulator_backend = self.provider.get_backend(self.target_backend)
        job1 = simulator_backend.run(atob, shots=1)
        job2 = simulator_backend.run(btoa, shots=1)
        
        raw_result1 = job1.result()
        raw_result2 = job2.result()
        if self.target_backend == 'ionq.qpu':
            r1, r2 = list(raw_result1.get_counts(atob).keys())[0], list(raw_result2.get_counts(btoa).keys())[0]
        else:
            # print(raw_result1)
            # print(raw_result1.to_dict())
            probdict1 = raw_result1.to_dict()['results'][0]['data']['probabilities']
            probdict2 = raw_result2.to_dict()['results'][0]['data']['probabilities']
            # print(probdict1)
            r1, r2 = pick_from_probabilities(probdict1), pick_from_probabilities(probdict2)

        s1, s2 = sum_score(r1), sum_score(r2)
        return r1, r2, s1, s2

    
    """
    I/O Functions
    """
    def get_buy_choice(self, pid):
        print(f"Player {pid+1} to buy minions")
        print(f"Current shop: {list(enumerate(self.current_shop))}")
        buy_choice = input(f"Selection? ")
        if buy_choice.isdigit() and int(buy_choice) in range(self.shopsize):
            self.buy_minion(pid, self.current_shop[int(buy_choice)])
            print(f"{self.current_shop[int(buy_choice)]} purchased!")
        else:
            print("Nothing purchased")


    def check_use_last_circuit(self, pid):
        if self.players[pid].circuit == None:
            return False
        
        print(self.players[pid].circuit)
        yes = input("Use last circuit? (y/n): ")
        if yes.lower() == 'y':
            return True
        else:
            return False

    def get_build_circuit(self, pid):
        avail = self.players[pid].minions.copy()
        sz = sum(avail.values())
        # circuit_data = []
        circuit = QuantumCircuit(self.lanes, self.lanes)
        while sz > 0:
            print(f"====================\nPlayer {pid+1} build phase.")
            print(f"Available minions: {avail}, total minions = {sz}")
            cmd = input("Place a gate: ")
            tokens = cmd.split(sep = " ")
            gatename = tokens[0].upper()
            if gatename not in avail.keys() or avail[gatename] == 0:
                print ("Not a valid choice!!")
                continue
            
            if gatename in SINGLE_QUBIT_GATES:
                if len(tokens) < 2 or not tokens[1].isdigit() or not int(tokens[1]) in range(self.lanes):
                    print ("Position input incorrect!!")
                    continue
                applySQG(circuit, gatename, [int(tokens[1])])
                # circuit_data.append((gatename, [int(tokens[1])]))
            elif gatename in TWO_QUBIT_GATES:
                if len(tokens) < 3 or not tokens[1].isdigit() or not int(tokens[1]) in range(self.lanes) or not tokens[2].isdigit() or not int(tokens[2]) in range(self.lanes) or int(tokens[1]) == int(tokens[2]):
                    print ("Position inputs incorrect!!")
                    continue
                applyTQG(circuit, gatename, [int(tokens[1]), int(tokens[2])])
                # circuit_data.append((gatename, [int(tokens[1]), int(tokens[2])]))
            avail[gatename] -= 1
            sz -= 1

            print(circuit)

        confirm = input("Confirm circuit build? (y/n): ")
        if confirm.lower() == 'y':
            self.players[pid].circuit = circuit
            return
        else:
            self.get_build_circuit(pid)


    def get_set_circuit(self, pid):
        if self.check_use_last_circuit(pid):
            return
        else:
            self.get_build_circuit(pid)

    """
    Game loop
    """
    def process_round(self):
        self.round += 1
        print(f"\n +++++++ ROUND {self.round} START +++++++ \n")
        for pid in range(len(self.players)):
            self.randomize_shop()
            self.get_buy_choice(pid)
            self.get_set_circuit(pid)
        

        print(f"\n +++++++ ROUND {self.round} BATTLE PHASE +++++++ \n")
        # assume two players
        r1, r2, s1, s2 = self.battle(0, 1)
        print(f"In Round A, {r1} was measured, giving a score of {s1} for Player {1}!")
        print(f"In Round B, {r2} was measured, giving a score of {s2} for Player {2}!")
        if s1 == s2:
            print("This battle was a draw!")
        else:
            print(f"The winner of this round is Player {1 if s1>s2 else 2}")
            if s1>s2:
                self.players[1].health -= 1
                if self.players[1].health == 0:
                    self.players.pop(1)
            else:
                self.players[0].health -= 1
                if self.players[0].health == 0:
                    self.players.pop(0)
            self.players_remaining -= 1

        
        print(f"\n +++++++ STATE AT THE END OF ROUND {self.round} +++++++ \n")
        self.pr_playerstate()

    def run_game(self):
        while self.players_remaining > 1:
            self.process_round()
        
        print (f"\n!!! THE WINNER IS Player {self.players[0].id} !!!\n")
        


    """
    Printing functions
    """
    def pr_playerstate(self):
        print("\n".join([str(player) for player in self.players]))


    def pr_boardstate(self):
        print(f"Minions in the pool: {self.pool}")


    def pr_state(self):
        print(f"State at round {self.round}:")
        self.pr_playerstate()
        self.pr_boardstate()
        print("=======")


# battle.py
# from os import abort
# import numpy as np
# import typing
# from qiskit import QuantumCircuit
# from qiskit.visualization import plot_histogram
# from qiskit.tools.monitor import job_monitor
# UnityEngine.Debug.Log("finished importiant qiskit")

# from azure.quantum.qiskit import AzureQuantumProvider
UnityEngine.Debug.Log("processed battlegrounds :o")


starting_pool = {'I':4, 'X':4, 'Y':4, 'Z':4, 'H':4, 'S':4, 'CX':4}
arena = Arena(2, 2, starting_pool, hero_pool=None)

# IMPORTANT! RETRIEVE CIRCUIT DESCRIPTIONS FROM C#
# UnityEngine.Debug.Log(UnityEngine.GameObject.Find("Button").GetComponents(typeof(Component)))
arr1 = UnityEngine.GameObject.Find("InvisibleText1").GetComponent("UnityEngine.UI.Text").text
arr2 = UnityEngine.GameObject.Find("InvisibleText2").GetComponent("UnityEngine.UI.Text").text

circuit_ind1 = arr1.split(" ")
circuit_ind2 = arr2.split(" ")

circuit_data1 = []
circuit_data2 = []

for ind, ele in enumerate(circuit_ind1):
  if ind % 2 == 0:
    li = []
    li.append(gate_translate(int(ele)))
  else:
    li.append(pos_translate(int(ele)))
    circuit_data1.append(li)

for ind, ele in enumerate(circuit_ind2):
  if ind % 2 == 0:
    li = []
    li.append(gate_translate(int(ele)))
  else:
    li.append(pos_translate(int(ele)))
    circuit_data2.append(li)


arena.build_circuit(0, circuit_data1)
arena.build_circuit(1, circuit_data2)
r1, r2, s1, s2 = arena.battle(0, 1)

if s1 > s2:
    winner = 0
elif s1 < s2:
    winner = 1
else:
    winner = -1

# WRITE WINNER TO C#
# UnityEngine.GameObject.Find("ScriptHolder").GetComponent("ButtonBehaviour").winner = winner

UnityEngine.Debug.Log("finished battle :o")
UnityEngine.Debug.Log(winner)

# --end--