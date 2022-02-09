def saywav_to_file(saywav_result,wavfile):
    b64 = saywav_result["wav_base64"]
    base64_message = b64.encode('utf-8')

    import base64

    with open(wavfile, 'wb') as file_to_save:
        decoded_image_data = base64.decodebytes(base64_message)
        file_to_save.write(decoded_image_data)
