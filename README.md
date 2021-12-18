# terminal_sjva

[SJVA](https://sjva.me/) 용 Terminal 모듈  
셸을 사용할 수 있습니다.

## 설치

SJVA의 "시스템 → 모듈 → 모듈 설정 → 모듈 목록"에서 terminal 모듈을 찾아 설치 버튼을 누르면 됩니다.

## 잡담

[xterm.js](https://xtermjs.org/) 라이브러리를 발견하고 신기해서 한번 만들어 봤습니다.  
찾아보니까 [pyxtermjs](https://github.com/cs01/pyxtermjs)라는 프로젝트가 있어서 해당 프로젝트의 코드를 많이 참고했습니다.

pty.fork()에서 pty.openpty()로 방식을 바꿨는데 터미널 사이즈 조절 명령어가 먹질 않아 화면이 깨지는 현상이 있습니다.  
화면이 깨져도 입력은 정상적으로 되고 있으니 당황하지 마시고 혹시 해결법을 알고 계시다면 도움 좀 부탁드립니다ㅠㅜ

## Changelog

v0.1.1

- 터미널을 fork하지 않고 새로 생성하는 방식으로 변경

v0.1.0

- 최초 공개  
  Thanks to [pyxtermjs](https://github.com/cs01/pyxtermjs)
