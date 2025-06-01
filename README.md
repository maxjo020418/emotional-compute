감컴 계획
====

### Components
1. 1차 인식 (카메라 인터페이스, coordination) 조영민 - `cam_backstage`
2. 2차 검사 (퀴즈, 추가 심전도 검사 등) 박희철 - `quiz_window`
3. dashboard 인터페이스 (infotainment sys.) 박승수 - `dashboard_window`s
4. 대리추천 시스템 (대리운전 선택 화면) 박지훈 - `daeri_window`

### What to use/do
- [x] 카메라 & 얼굴인식 - openCV & deepface pipeline
- [x] UI - PyQT5 framework & foundations
- [x] quiz interface
- [ ] Scraping for demo interface(?) - requests/bs4 OR Selenium/bs4

>[!NOTE]
>카메라는 시스템에서 인식되는 1번 카메라를 사용함.
>인식 순번에 따라 Screen cap. 등으로 인식될수도 있음.
>`640x480`화질로 잘림, 카메라에 따라 잘리거나 눌릴수도 있음 (일반적 웹캠 화질에 맞춤)
