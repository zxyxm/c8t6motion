"""Generate editable vector schematics and PDF. Coordinates in drawing units."""
from pathlib import Path
import csv, html, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = Path(__file__).resolve().parents[1]
W,H=1400,990
default_font = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'simhei.ttf'
pdfmetrics.registerFont(TTFont('SchematicChinese', os.environ.get('SCHEMATIC_CJK_FONT', str(default_font))))
pdf=canvas.Canvas(str(OUT/'四轴运动控制底板_V0.1.pdf'), pagesize=(W,H))
svg=[]
netrows=[]
def line(x,y,a,b):
    pdf.setStrokeColor(HexColor('#175a78')); pdf.setLineWidth(1.4); pdf.line(x,H-y,a,H-b)
    svg.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="#175a78" stroke-width="1.4"/>')
def text(x,y,s,size=12,color='#202d3c',chinese=False):
    pdf.setFillColor(HexColor(color)); pdf.setFont('SchematicChinese' if chinese else 'Helvetica',size); pdf.drawString(x,H-y,s)
    family = 'SimHei,Microsoft YaHei,Noto Sans CJK SC,sans-serif' if chinese else 'Arial,sans-serif'
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}">{html.escape(s)}</text>')
def annotation(x,y,s,size=13):
    text(x,y,s,size,'#b51f27',chinese=True)
def box(x,y,w,h):
    for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,c,d)
def dot(x,y):
    pdf.setFillColor(HexColor('#175a78'));pdf.circle(x,H-y,3,stroke=0,fill=1)
    svg.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#175a78"/>')
def label(x,y,s):text(x,y-6,s,11,'#a33328')
def ground(x,y):
    line(x,y,x,y+10)
    for w,d in [(12,10),(8,15),(4,20)]:line(x-w,y+d,x+w,y+d)
def resistor(x,y,ref,val):
    line(x,y,x+16,y);box(x+16,y-6,42,12);line(x+58,y,x+75,y)
    text(x+16,y-14,ref+' '+val,10)
def cap(x,y,ref,val):
    line(x,y,x,y+24);line(x-12,y+24,x+12,y+24);line(x-12,y+30,x+12,y+30);line(x,y+30,x,y+55)
    text(x+18,y+26,ref+' '+val,10);ground(x,y+55)
def start(n,title,subtitle):
    global svg
    svg=[];box(20,20,W-40,H-40)
    text(44,58,'C8T6 MOTION / 4 AXIS BASEBOARD',22)
    text(44,86,title,18);text(44,110,subtitle,11)
    line(40,130,W-40,130)
    line(40,920,W-40,920)
    text(44,945,'V0.1 - REVIEW DRAFT | 2026-11-19 | 5V common-anode optocoupler drivers | No PCB / no ERC yet',11)
    text(1250,945,f'{n} / 3',12)
def finish(n):
    (OUT/'源文件'/f'sheet{n}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="990" viewBox="0 0 1400 990">'+''.join(svg)+'</svg>',encoding='utf-8')
    pdf.showPage()
def connector(ref,title,x,y,nets,pins=None):
    text(x,y-28,ref+'  '+title,13);box(x,y,130,len(nets)*25+12)
    for i,net in enumerate(nets):
        yy=y+22+i*25;num=pins[i] if pins else i+1
        text(x+10,yy+4,str(num),10);line(x+40,yy,x+165,yy);label(x+170,yy,net)
        netrows.append((ref,num,net))

start(1,'01 / Coreboard sockets and power','Socket numbering follows H4 / H5 in supplied coreboard schematic. Verify physical orientation before PCB layout.')
left=['VBAT','PC13','PC14','PC15','X_PUL_PA0','PA1','PA2','PA3','PA4','PA5','Y_PUL_PA6','PA7','PB0','PB1','PB10','PB11','NRST','+3V3_CORE','GND','GND']
right=['+3V3_CORE','GND','+5V_CORE','PB9','PB8','PB7','Z_PUL_PB6','PB5','PB4','PB3','PA15','PA12_USB_DP','PA11_USB_DM','UART_RX_PA10','UART_TX_PA9','A_PUL_PA8','A_DIR_PB15','Z_DIR_PB14','Y_DIR_PB13','X_DIR_PB12']
connector('JH4','1x20 socket / core H4',60,190,left)
connector('JH5','1x20 socket / core H5',460,190,right)
text(60,760,'Use 2.54 mm sockets; row spacing and pin-1 direction require actual board measurement.',12)
text(60,786,'Unused signal nets are reserved only. PC14/PC15 serve the on-board 32.768 kHz crystal.',12)
text(60,812,'USB PA11/PA12 and SWD PA13/PA14 remain available on the coreboard.',12)
connector('J1','5V DC IN / 3.81 mm',875,190,['+5V_IN','GND'])
line(900,340,940,340);label(900,340,'+5V_IN');box(940,332,70,16);text(940,320,'F1 PTC 0.5A',11);line(1010,340,1240,340);label(1160,340,'+5V_OUT')
cap(1060,340,'C1','100uF/10V');text(1040,359,'+',12);cap(1220,340,'C2','100nF')
dot(1060,340);dot(1220,340)
line(860,435,1340,435)
connector('J7','24V DC IN / 3.81 mm',875,490,['+24V_IN','GND'])
annotation(875,480,'J7 接稳压 24V，降压后单独给核心板供电。')
# Fuse and local input capacitor precede the SIP3 buck module.
line(875,625,935,625);label(875,625,'+24V_IN')
box(935,618,46,14);text(915,604,'F2 T1.6A',10)
line(981,625,1090,625);label(986,625,'+24V_FUSED');dot(1010,625)
cap(1010,625,'C3','22uF/50V');text(989,645,'+',12)
box(1090,600,120,64);text(1090,585,'U1 TSR 1-2450',13)
text(1096,629,'1 IN',10);text(1165,629,'3 OUT',10);text(1134,654,'2 GND',10)
ground(1150,664)
line(1210,625,1330,625);label(1240,625,'+5V_REG')
line(875,745,980,745);label(875,745,'+5V_REG')
box(980,736,65,18);text(980,724,'JP1 1-2',11)
line(1045,745,1320,745);label(1105,745,'+5V_CORE')
annotation(875,789,'插上 JP1 后，5V 经 H5 第 3 脚为核心板供电。')
annotation(875,815,'接入带供电的 USB 前，先拔掉 JP1 跳帽。')
annotation(875,841,'J1 仍需接 5V 为驱动器光耦供电。两路共地。')
annotation(875,867,'J7 按极性接线。模块输入瞬态不得超过 36V。')
annotation(60,181,'核心板两侧插座（对应原图 H4、H5）')
annotation(875,181,'J1 仅接稳压 5V，供四轴驱动器光耦。')
annotation(60,850,'制作 PCB 前，实测两排插座间距并确认 1 脚方向。')
finish(1)

start(2,'02 / Four-axis PUL and DIR outputs','J2-J5: green pluggable screw terminal, pitch 3.81 mm, 4 positions. All plus terminals connect to +5V_OUT.')
axes=[('X','PA0','PB12','TIM2_CH1','JH4.5','JH5.20'),('Y','PA6','PB13','TIM3_CH1','JH4.11','JH5.19'),('Z','PB6','PB14','TIM4_CH1','JH5.7','JH5.18'),('A','PA8','PB15','TIM1_CH1','JH5.16','JH5.17')]
for i,(a,p,d,t,pp,dp) in enumerate(axes):
    ox=50+(i%2)*660;oy=165+(i//2)*355
    text(ox,oy,f'{a} AXIS / {t} / {pp}',14)
    for j,(typ,gpio,src) in enumerate([('PUL',p,pp),('DIR',d,dp)]):
        y=oy+70+j*130;x=ox
        idx=i*2+j+1;ref='Q'+str(idx);rn=idx*2-1
        label(x,y,f'{a}_{typ}_{gpio}');line(x,y,x+100,y);resistor(x+100,y,'R'+str(rn),'100R')
        line(x+175,y,x+245,y);dot(x+200,y)
        # 10k gate pull-down represented as vertical resistor
        line(x+200,y,x+200,y+16);box(x+194,y+16,12,26);line(x+200,y+42,x+200,y+49);ground(x+200,y+49)
        text(x+115,y+36,'R'+str(rn+1)+' 10k',10)
        # N-channel enhancement MOSFET; G=1 S=2 D=3
        line(x+245,y-19,x+245,y+19);line(x+253,y-18,x+253,y+18)
        line(x+253,y-15,x+280,y-15);line(x+280,y-15,x+280,y-40)
        line(x+253,y+15,x+280,y+15);line(x+280,y+15,x+280,y+49);ground(x+280,y+49)
        text(x+230,y+5,'1',9);text(x+284,y-20,'3 D',9);text(x+284,y+30,'2 S',9)
        # body diode from source to drain, cathode at drain
        line(x+280,y-15,x+302,y-15);line(x+302,y-15,x+302,y-3)
        line(x+296,y-3,x+308,y-3);line(x+296,y+7,x+302,y-3);line(x+308,y+7,x+302,y-3);line(x+296,y+7,x+308,y+7)
        line(x+302,y+7,x+302,y+15);line(x+302,y+15,x+280,y+15)
        label(x+310,y-40,f'{a}_{typ}_N');line(x+280,y-40,x+320,y-40)
        text(x+230,y+76,ref+' AO3400A',11)
        netrows.extend([(ref,1,f'{a}_{typ}_G'),(ref,2,'GND'),(ref,3,f'{a}_{typ}_N'),('R'+str(rn),1,f'{a}_{typ}_{gpio}'),('R'+str(rn),2,f'{a}_{typ}_G'),('R'+str(rn+1),1,f'{a}_{typ}_G'),('R'+str(rn+1),2,'GND')])
    connector('J'+str(i+2),'3.81 / 4P',ox+405,oy+20,['+5V_OUT',f'{a}_PUL_N','+5V_OUT',f'{a}_DIR_N'])
    text(ox+405,oy+230,'1 PUL+   2 PUL-',10);text(ox+405,oy+252,'3 DIR+   4 DIR-',10)
    annotation(ox+405,oy+209,f'{a} 轴 3.81 mm 绿色端子',12)
    annotation(ox+405,oy+278,'1、3 脚接 5V 共阳',12)
    annotation(ox+405,oy+298,'2、4 脚由 MOS 管下拉',12)
annotation(50,853,'PUL 用定时器通道，DIR 用普通 GPIO。TIM1 至 TIM4 各控制一轴，可独立调速。')
annotation(750,853,'普通 PWM 模式下，同一定时器的多个通道共用频率。')
text(50,890,'GPIO high -> MOSFET ON -> driver optocoupler ON. GPIO low/reset -> OFF. No ENA connection in V0.1.',12)
finish(2)

start(3,'03 / Host UART and electrical interface notes','USART1: PA9 = TX, PA10 = RX. No remapping. 3.3V TTL only, shared GND, USB-to-UART adapter required for PC.')
label(70,200,'UART_TX_PA9');line(70,200,235,200);resistor(235,200,'R17','100R');line(310,200,470,200);label(390,200,'HOST_RX')
label(70,390,'UART_RX_PA10');line(70,390,235,390);resistor(235,390,'R18','100R');line(310,390,470,390);label(390,390,'HOST_TX')
line(190,390,190,320);dot(190,390);box(184,275,12,45);line(190,275,190,250);label(170,250,'+3V3_CORE');text(205,300,'R19 10k',11)
connector('J6','HOST UART / 3.81 mm 3P',650,200,['HOST_RX','HOST_TX','GND'])
text(650,330,'1 = card TX -> adapter RX',13)
text(650,357,'2 = card RX <- adapter TX (3.3V)',13)
text(650,384,'3 = card GND <-> adapter GND',13)
annotation(650,422,'上位机使用 3.3V USB 转 TTL 模块。')
annotation(650,448,'TX 与 RX 交叉连接，GND 相连，VCC 不接。')
annotation(850,535,'先设定 DIR，再发 PUL，时序按驱动器手册。')
annotation(850,564,'确认驱动器支持 5V 共阳输入，并按手册确认限流。')
text(70,480,'OUTPUT CONTRACT',15)
notes=[
 '1. Drivers must accept 5V common-anode PUL/DIR inputs with internal current-limiting resistors.',
 '2. If the driver requires an external resistor, fit the value specified by its datasheet in the cable.',
 '3. Do not connect these outputs to 12V/24V control terminals or bare LEDs without a series resistor.',
 '4. PUL_N and DIR_N are sinking outputs, not differential line-driver outputs. Do not use as RS-422.',
 '5. Each axis has its own timer period. Actual maximum frequency and pulse width await driver testing.',
 '6. Initialize DIR first, then enable PUL; idle PUL GPIO low. Meet driver DIR setup/hold timing.',
 '7. Reset gate pull-downs turn MOSFETs off. This is not an emergency-stop safety circuit.',
 '8. UART: use short local cable. No RS-232/RS-485 transceiver, galvanic isolation or surge protection.',
 '9. Do not wire a 5V UART adapter VCC to this connector; only TX/RX/GND are provided.',
 '10. Coreboard socket pitch/row spacing and terminal orientation remain to be verified before PCB.',
 '11. Limit/home, enable, emergency stop and spindle interfaces are outside this initial draft.',
 '12. Device selection checked against ST STM32F103x8/xB datasheet and AOS AO3400A datasheet.'
]
for i,s in enumerate(notes):text(70,515+i*29,s,12)
netrows.extend([('R17',1,'UART_TX_PA9'),('R17',2,'HOST_RX'),('R18',1,'UART_RX_PA10'),('R18',2,'HOST_TX'),('R19',1,'+3V3_CORE'),('R19',2,'UART_RX_PA10'),('F1',1,'+5V_IN'),('F1',2,'+5V_OUT'),('JP1',1,'+5V_REG'),('JP1',2,'+5V_CORE'),('C1',1,'+5V_OUT'),('C1',2,'GND'),('C2',1,'+5V_OUT'),('C2',2,'GND')])
netrows.extend([('F2',1,'+24V_IN'),('F2',2,'+24V_FUSED'),('C3',1,'+24V_FUSED'),('C3',2,'GND'),('U1',1,'+24V_FUSED'),('U1',2,'GND'),('U1',3,'+5V_REG')])
finish(3);pdf.save()
with (OUT/'连接表.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['器件','引脚','网络']);w.writerows(netrows)
with (OUT/'引脚分配.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['轴','PUL引脚','定时器','核心板排针','DIR引脚','核心板排针'])
    for a,p,d,t,pp,dp in axes:w.writerow([a,p,t,pp,d,dp])
    w.writerow(['UART TX','PA9','USART1','JH5.15','','']);w.writerow(['UART RX','PA10','USART1','JH5.14','',''])
with (OUT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['位号','数量','型号/参数','封装/说明'])
    w.writerows([['JH4,JH5',2,'1x20排母','2.54mm；排距待实测'],['J1',1,'绿色接线端子 2P','3.81mm'],['J2-J5',4,'绿色接线端子 4P','3.81mm'],['J6',1,'绿色接线端子 3P','3.81mm'],['Q1-Q8',8,'AO3400A','SOT-23；1=G,2=S,3=D'],['R1,R3,R5,R7,R9,R11,R13,R15,R17,R18',10,'100R 1%','0603'],['R2,R4,R6,R8,R10,R12,R14,R16,R19',9,'10k 1%','0603'],['C1',1,'100uF/10V','极性电容；正极接+5V_OUT'],['C2',1,'100nF/16V X7R','0603'],['F1',1,'PTC 0.5A hold','型号及温度降额待定'],['JP1',1,'1x2排针+跳帽','2.54mm']])
    w.writerows([
        ['J7',1,'绿色接线端子 2P','3.81mm，标注 24V/GND'],
        ['U1',1,'TRACO POWER TSR 1-2450','SIP3，1=VIN，2=GND，3=VOUT'],
        ['C3',1,'22uF/50V','极性电容，靠近 U1 输入和地'],
        ['F2',1,'T1.6A 慢断保险丝及座','直流额定电压至少 36V，按电源短路能力选分断能力'],
    ])
print(OUT)
