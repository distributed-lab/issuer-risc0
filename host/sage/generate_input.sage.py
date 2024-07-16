

# This file was *autogenerated* from the file host/sage/generate_input.sage
from sage.all_cmdline import *   # import sage library

_sage_const_32 = Integer(32); _sage_const_2 = Integer(2); _sage_const_4 = Integer(4); _sage_const_1 = Integer(1); _sage_const_0 = Integer(0)
import json
import os
import hashlib
from datetime import datetime
from random import (randbytes, shuffle)

DIGEST_BYTES = _sage_const_32   # bytes for SHA-256
BLINDER_BYTES = _sage_const_32 
SALT_BYTES = _sage_const_32 
DUPLICATE_COUNT = _sage_const_2 
MERKLE_LEAVES_COUNT = _sage_const_4 

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves
        self.tree = self.build_tree(leaves)
    
    def build_tree(self, leaves):
        tree = [leaves]
        current_level = leaves
        while len(current_level) > _sage_const_1 :
            next_level = []
            for i in range(_sage_const_0 , len(current_level), _sage_const_2 ):
                left = current_level[i]
                right = current_level[i + _sage_const_1 ] if i + _sage_const_1  < len(current_level) else left
                next_level.append(self.hash_pair(left, right))
            tree.append(next_level)
            current_level = next_level
        return tree

    def hash_pair(self, left, right):
        hasher = hashlib.sha256()
        hasher.update(left + right)
        return hasher.digest()

    def get_root(self):
        return self.tree[-_sage_const_1 ][_sage_const_0 ] if self.tree else None

    def get_proof(self, leaf):
        try:
            index = self.leaves.index(leaf)
        except ValueError:
            raise ValueError("Leaf not found in the tree")

        branch = []
        level_index = index
        for level in self.tree[:-_sage_const_1 ]:
            level_length = len(level)
            if level_index % _sage_const_2  == _sage_const_0  and level_index + _sage_const_1  < level_length:
                branch.append(level[level_index + _sage_const_1 ])
            elif level_index % _sage_const_2  == _sage_const_1 :
                branch.append(level[level_index - _sage_const_1 ])
            level_index //= _sage_const_2 

        return {"index": index, "branch": [b.hex() for b in branch]}

def hash_bytes(byte_list):
    hasher = hashlib.sha256()
    hasher.update(byte_list)
    return hasher.digest()

# Generate random values for document_hash, blinder, and salts
document_hash = randbytes(DIGEST_BYTES)
blinder = randbytes(BLINDER_BYTES)
salts = [randbytes(SALT_BYTES) for _ in range(DUPLICATE_COUNT)]

# Compute nullifiers
nullifiers = [hash_bytes(blinder + salt + document_hash) for salt in salts]

# Generate additional leaves and shuffle
leaves = nullifiers + [randbytes(DIGEST_BYTES) for _ in range(MERKLE_LEAVES_COUNT - DUPLICATE_COUNT)]
shuffle(leaves)

# Create Merkle tree and get proofs
tree = MerkleTree(leaves)
root = tree.get_root()
proofs = [tree.get_proof(nullifier) for nullifier in nullifiers]

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
test_values_dir = os.path.join(script_dir, '..', 'test_values')

# Generate a unique filename based on the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

input_path = os.path.join(test_values_dir, f"input_{timestamp}.json")
output_path = os.path.join(test_values_dir, f"expected_journal_{timestamp}.json")

os.makedirs(test_values_dir, exist_ok=True)

input_data = {
    "document_hash": document_hash.hex(),
    "blinder": blinder.hex(),
    "salts": [salt.hex() for salt in salts],
    "merkle_root": root.hex(),
    "merkle_proofs": proofs
}

with open(input_path, "w") as f:
    json.dump(input_data, f, indent=_sage_const_4 )

output_data = {
    "blinder_commitment": hash_bytes(blinder).hex(),
    "document_commitment": hash_bytes(document_hash + blinder).hex(),
    "total_duplicates": int(DUPLICATE_COUNT)
}

with open(output_path, "w") as f:
    json.dump(output_data, f, indent=_sage_const_4 )

print("Generated input JSON. Path:", input_path)
print("Generated expected journal JSON. Path:", output_path)
