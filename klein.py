# TODO: testing of encryption



SBOX =[0x7, 0x4, 0xA, 0x9, 0x1, 0xF, 0xB, 0x0, 0xC, 0x3, 0x2, 0x6, 0x8, 0xE, 0xD, 0x5]

def round_function(state, round_key, round_no, n):
    state = AddRoundKey(state, round_key, n)
    state = SubNibbles(state, n)
    state = RotateNibbles(state, n)
    state = MixNibbles(state, n)
    next_round_key = KeySchedule(round_key, round_no, n)
    return state, next_round_key

def AddRoundKey(state, round_key, n):
    to_be_removed = n - 64
    state = state ^ (round_key >> to_be_removed)
    return state & (0xFFFFFFFFFFFFFFFF)

def substitue(state, i, n):
    offset = n - (i+1)*4
    nibble = (state >> offset) & 0xF
    return (state & ~(0xF << offset) | (SBOX[nibble] << offset) )


def SubNibbles(state, n):
    for i in range(16):
        state = substitue(state, i, n)
    return state

def RotateNibbles(state, n):
    state = ((state << 16) | (state >> 48)) & 0xFFFFFFFFFFFFFFFF
    
 def mul2or3(x, n):  # this is not nearly as generic as galoisMult
            x = (x << 1) if n == 2 else ((x << 1) ^ x)
            if x > 0xFF:
                return (x ^ 0x1B) & 0xFF
            return x
        
def MixCols(half_state):
        mask = 0xFF 
        z01 = (half_state >> 24) & mask
        z23 = (half_state >> 16) & mask
        z45 = (half_state >> 8) & mask
        z67 =  half_state & mask
        
        c01 = mul2or3(z01, 2) ^ mul2or3(z23, 3) ^ z45 ^ z67
        c23 = z01 ^ mul2or3(z23, 2) ^ mul2or3(z45, 3) ^ z67
        c45 = z01 ^ z23 ^ mul2or3(z45, 2) ^ mul2or3(z67, 3)
        c67 = mul2or3(z01, 3) ^ z23 ^ z45 ^ mul2or3(z67, 2)
        return c01 << 24 | c23 << 16 | c45 << 8 | c67
    
def MixNibbles(state, n):
    c1 = MixCols(state >> 32)
    mask0 = 0xFFFFFFFF
    c0 = MixCols(state & mask0)
    return (c1 << 32) | c0

def KeySchedule(prev_key, round_no, n):
    a = prev_key >> n//2
    b = prev_key & int('F'*n//8)
    a_dash = ((a << 8) | (a >> n-8)) & int('F'*n//8)
    b_dash = ((b << 8) | (b >> n-8)) & int('F'*n//8)
    a_dash_dash = b_dash
    b_dash_dash = a_dash ^ b_dash 
    a_dash_dash = a_dash_dash ^ (round_no << (n//2 - 24))
    for i in range(2,6):
        b_dash_dash = substitue(b_dash_dash, i, n//2)
    return (a_dash_dash << n/2) | b_dash_dash

def KLEIN_encrypt(plaintext, key_len, nof_rounds, init_key):
    state = plaintext
    round_key = init_key
    for i in range(1, nof_rounds+1):
        state, round_key = round_function(state, round_key, i, key_len)
    state = AddRoundKey(state, round_key, n)
    return state
