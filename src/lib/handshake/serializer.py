class MessageSerializer:
    @staticmethod
    def _bool_to_byte(flag: bool) -> bytes:
        """
        Convert boolean to byte:
        True  → b'\x01'
        False → b'\x00'
        """
        return (1).to_bytes(1, byteorder='big') if flag else (
            0).to_bytes(1, byteorder='big')

    @staticmethod
    def _byte_to_bool(b: bytes) -> bool:
        """
        Convert byte to boolean:
        b'\x01' → True
        b'\x00' → False
        """
        return bool(b[0])

    @staticmethod
    def first_msg_to_bytes(num_seq, client_prot_type, app_metadata) -> bytes:

        syn = MessageSerializer._bool_to_byte(True)
        num_seq_b = num_seq.to_bytes(1, byteorder='big')  # 1 byte
        client_prot_type_b = client_prot_type.encode()  # 2 bytes
        app_metadata_b = app_metadata.encode()  # 1 fixed + var
        return syn + num_seq_b + client_prot_type_b + app_metadata_b

    @staticmethod
    def first_msg_from_bytes(client_data: bytes) -> tuple:
        syn = MessageSerializer._byte_to_bool(client_data[0:1])
        num_seq = int.from_bytes(client_data[1:2], byteorder='big')
        client_prot_type = client_data[2:4].decode()
        app_metadata = client_data[4:].decode()

        return syn, num_seq, client_prot_type, app_metadata

    @staticmethod
    def second_msg_to_bytes(serv_num_seq, client_num_seq) -> bytes:
        syn_b = MessageSerializer._bool_to_byte(True)
        client_num_seq_b = client_num_seq.to_bytes(1, byteorder='big')
        serv_num_seq_b = serv_num_seq.to_bytes(1, byteorder='big')
        return syn_b + serv_num_seq_b + client_num_seq_b

    @staticmethod
    def second_msg_from_bytes(srv_data: bytes) -> tuple:
        srv_num_seq = int.from_bytes(srv_data[1:2], byteorder='big')
        ack = int.from_bytes(srv_data[2:3], byteorder='big')
        return srv_num_seq, ack

    @staticmethod
    def third_msg_to_bytes(serv_num_seq) -> bytes:
        syn_b = MessageSerializer._bool_to_byte(True)
        ack = serv_num_seq.to_bytes(1, byteorder='big')
        return syn_b + ack

    @staticmethod
    def third_msg_from_bytes(client_data: bytes) -> tuple:
        syn = MessageSerializer._byte_to_bool(client_data[0:1])
        ack = int.from_bytes(client_data[1:2], byteorder='big')
        return syn, ack

    @staticmethod
    def _is_about_handhshake(data: bytes) -> bool:
        return MessageSerializer._byte_to_bool(data[0:1])
