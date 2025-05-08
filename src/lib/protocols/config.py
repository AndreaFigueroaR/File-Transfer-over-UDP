# BEST CONFIG WITHOUT DELAY
# [10% (5%/5%) Packet loss] config
NUM_ATTEMPTS = 20
TIMEOUT = 0.01

# CONFIG NEEDED WHEN DELAY SET
# [10% (5%/5%) Packet loss] + [5ms 2ms delay] config
# NUM_ATTEMPS = 80
# TIMEOUT = 0.1

MAX_WIN_SIZE = 4

" SYN: 1 byte"
" Checksum: 4 bytes"
" Número de secuencia: 1 byte"
" Id de paquete: 2 bytes"
" TOTAL = 8 bytes"
SR_SEGMENT_HEADER_SIZE = 8
