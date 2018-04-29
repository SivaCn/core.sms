#!/usr/bin/python

import time
import serial


class SMS(object):

    def __init__(self, device_port, baudrate, timeout):

        _params = {
            'port': device_port,
        }

        if baudrate:
            _params.update({'baudrate': baudrate})

        if timeout:
            _params.update({'timeout': timeout})

        self.port = serial.Serial(**_params)

    def does_gsm_device_work(self):

        self.port.write('AT\r')

        response = self.get_response()
        if 'OK' in response:
            return True, response
        return False, response

    def set_device_on_sms_mode(self):

        self.port.write("AT+CMGF=1\r")

        response = self.get_response()
        if 'OK' in response:
            return True, response
        return False, response

    def send(self, message, recipient):

        self.port.write('AT+CMGS="{}"\r\n'.format(recipient))
        time.sleep(2)
        self.port.write(message)
        self.port.write(chr(26))

        response = self.get_response()
        if 'OK' in response:
            return True, response
        return False, response

    def get_response(self, wait_time=10):

        output = ''

        start_time = time.time()
        while start_time + wait_time >= time.time():
            output += self.port.readline()

        return output


class SendSMS(SMS):

    def __init__(self, device_port=None, baudrate=None, timeout=5):
        super(self.__class__, self).__init__(
            device_port=device_port, baudrate=baudrate, timeout=timeout
        )

    def send(self, message, recipient):
        import pdb; pdb.set_trace()
        result, response = self.does_gsm_device_work()
        if not result:
            print response
            raise Exception("The Connected GSM Device is not working.")

        result, respone = self.set_device_on_sms_mode()
        if not result:
            print response
            raise Exception("Unable to set the GSM device on SMS mode.")

        import pdb; pdb.set_trace()
        result, response = super(self.__class__, self).send(message, recipient)
        if not result:
            print response
            raise Exception("Unable to send SMS.")


sim = SendSMS('/dev/ttyS0')

sim.send('HI chellakutty', '9742398830')

sim.close()
