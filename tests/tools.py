# A collection of tools for querying the state of the SCHIP emulator.
def hex_dump_generator(memory, nbytes):
    """Return nbytes of memory, formatted as a hex string."""
    start_byte = 0
    total_bytes = memory.size

    while start_byte < total_bytes:
        memory_slice = memory[start_byte : start_byte + nbytes]
        hex_string = " ".join("{:02x}".format(s) for s in memory_slice) + "\n"

        yield hex_string
        start_byte += nbytes  # Update next row


def hex_dump(machine, cols=32):
    """Returns a hexdump string of memory."""
    return "".join(s for s in hex_dump_generator(machine.memory, cols))


def print_hex_dump(machine, cols=32):
    print("{!s}".format(hex_dump(machine, cols)))


def write_hex_dump(machine, cols=32):
    """Write hexdump of memory"""
    fname = "game"
    with open(fname + ".hexdmp", "w+") as f:
        f.write(hex_dump(machine, cols))
