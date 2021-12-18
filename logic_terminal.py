import traceback
import os
import platform
import pty
import subprocess
import base64
import select
import struct
import fcntl
import termios
from shlex import split

from flask import request, render_template, jsonify

from plugin import LogicModuleBase
from mod import P
from framework import socketio

name = 'terminal'
logger = P.logger
ModelSetting = P.ModelSetting
package_name = P.package_name


class LogicTerminal(LogicModuleBase):
    db_default = {
        f'{name}_db_version': '1',
        f'{name}_shell': os.environ.get('SHELL', 'bash') if platform.system() != 'Windows' else 'powershell'
    }

    pty_list = {}

    def __init__(self, p):
        super(LogicTerminal, self).__init__(p, 'terminal')
        self.name = name

    def process_menu(self, sub, req):
        try:
            arg = {
                'package_name': package_name,
                'sub': name,
                'sub2': sub
            }

            if sub == 'setting':
                arg.update(ModelSetting.to_dict())

            elif sub == 'terminal':
                pass

            return render_template(f'{package_name}_{name}_{sub}.html', arg=arg)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return render_template('sample.html', title=f'{package_name} - {sub}')

    # 터미널 실행
    @staticmethod
    @socketio.on('connect', namespace=f'/{package_name}/{name}')
    def connect():
        try:
            logger.debug('socketio: /%s/%s, connect, %s',
                         package_name, name, request.sid)
            cmd = split(ModelSetting.get(f'{name}_shell'))
            (master, slave) = pty.openpty()  # 터미널 생성
            popen = subprocess.Popen(
                cmd, stdin=slave, stdout=slave, stderr=slave, start_new_session=True)  # 셸 실행
            logger.debug('cmd: %s, child pid: %s', cmd, popen.pid)
            LogicTerminal.pty_list[request.sid] = {
                'popen': popen, 'master': master, 'slave': slave}
            socketio.start_background_task(
                LogicTerminal.output_emit, master, request.sid)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 터미널 종료
    @staticmethod
    @socketio.on('disconnect', namespace=f'/{package_name}/{name}')
    def disconnect():
        try:
            logger.debug('socketio: /%s/%s, disconnect, %s',
                         package_name, name, request.sid)
            popen = LogicTerminal.pty_list[request.sid]['popen']
            if popen.poll():
                popen.kill()
            os.close(LogicTerminal.pty_list[request.sid]['master'])
            os.close(LogicTerminal.pty_list[request.sid]['slave'])
            del LogicTerminal.pty_list[request.sid]
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 커맨드 입력
    @staticmethod
    @socketio.on('input', namespace=f'/{package_name}/{name}')
    def input(data):
        try:
            logger.debug('socketio: /%s/%s, input, %s, %s',
                         package_name, name, request.sid, data)
            fd = LogicTerminal.pty_list[request.sid]['master']
            os.write(fd, base64.b64decode(data))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 크기조절
    @staticmethod
    @socketio.on('resize', namespace=f'/{package_name}/{name}')
    def resize(data):
        try:
            logger.debug('socketio: /%s/%s, resize, %s, %s',
                         package_name, name, request.sid, data)
            fd = LogicTerminal.pty_list[request.sid]['master']
            LogicTerminal.set_winsize(fd, data['rows'], data['cols'])
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 출력 전송
    @staticmethod
    def output_emit(fd, room):
        try:
            max_read_bytes = 1024 * 20
            while True:
                socketio.sleep(0.01)
                if select.select([fd], [], [], 0)[0]:
                    output = os.read(fd, max_read_bytes).decode()
                    socketio.emit(
                        'output', output, namespace=f'/{package_name}/{name}', room=room)
        except OSError as e:    # 터미널 종료
            pass
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    # 터미널 사이즈 설정
    @staticmethod
    def set_winsize(fd, row, col, xpix=0, ypix=0):
        winsize = struct.pack('HHHH', row, col, xpix, ypix)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
