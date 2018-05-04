
import time
import serial
import argparse
import multiprocessing


class SMS(object):

    def __init__(self, device_port, baudrate, timeout):

        _params = {
            'port': device_port,
        }

        if baudrate:
            _params.update({'baudrate': baudrate})

        if timeout:
            _params.update({'timeout': timeout})

        if getattr(self, 'port', None):
            if self.port.isOpen():
                self.close()

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
        while 'ok' not in output.lower() and (start_time + wait_time >= time.time()):
            output += self.port.readline()

        return output

    def close(self):
        self.port.close()


class SendSMS(SMS):

    def __init__(self, device_port=None, baudrate=None, timeout=10):
        super(self.__class__, self).__init__(
            device_port=device_port, baudrate=baudrate, timeout=timeout
        )

    def send(self, message, recipient):

        message = str(message)
        recipient = str(recipient)

        response_flag = False
        response_message = 'Not yet initiated'

        try:
            result, response = self.does_gsm_device_work()
            if not result:
                raise Exception("The Connected GSM Device is not working.")

            result, respone = self.set_device_on_sms_mode()
            if not result:
                raise Exception("Unable to set the GSM device on SMS mode.")

            result, response = super(self.__class__, self).send(message, recipient)
            if not result:
                raise Exception("Unable to send SMS.")

        except Exception as error:
            response_flag = False
            response_message = str(error)

        else:
            response_flag = True
            response_message = None

        self.close()

        return response_flag, response_message


def main():

    example_invocation = """This is a test utility to send SMS

    Usage:
        python client.py --port /dev/ttyS0 --message "Hello World" --number 99999 88888

    """


    parser = argparse.ArgumentParser(
        description=example_invocation,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--port', '-p',
                        required=True,
                        help='serial port')

    parser.add_argument('--message', '-m',
                        required=True,
                        help='Text message to be sent')

    parser.add_argument('--number', '-n',
                        required=True,
                        help='mobile number to send SMS')


    cmd_args = parser.parse_args()

    sim = SendSMS(cmd_args.port)
    result, message = sim.send(cmd_args.message, cmd_args.number)
    sim.close()

    _msg = '{} sms to {} {}'
    return _msg.format(
        'Successfully sent' if result else 'Failed to send',
        cmd_args.number,
        '' if result else message
    )


def test_sms_send():

    # Start send sms as a process
    p = multiprocessing.Process(target=main)
    p.start()

    # Wait for 20 seconds or until process finishes
    p.join(20)

    # If thread is still active
    if p.is_alive():
        print "sending SMS... [Failed]"
        print "running... out of time..."
        print
        print "Killed semd_sms process [OK]"

        # Terminate
        p.terminate()
        p.join()

    else:
        print "sending SMS... [Success]"
        print


if __name__ == '__main__':

    test_sms_send()
