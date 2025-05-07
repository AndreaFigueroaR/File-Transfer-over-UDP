FIRST_SN = 0
NUM_ATTEMPS = 20

" SYN: 1 byte"
" FIN: 1 byte"
" Checksum: 4 bytes"
" Número de secuencia: 1 byte"
" TOTAL = 7 bytes"
SW_SEGMENT_HEADER_SIZE = 7

" ACK: 1 byte"
SW_ACK_SIZE = 1

" SYN: 1 byte"
" FIN: 1 byte"
SW_ACK_HEADER_SIZE = 2

" SYN: 1 byte"
" Checksum: 4 bytes"
" Número de secuencia: 1 byte"
" Id de paquete: 2 bytes"
" TOTAL = 8 bytes"
SR_SEGMENT_HEADER_SIZE = 8
