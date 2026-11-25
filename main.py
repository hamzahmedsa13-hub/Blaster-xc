import pygame,random,sys,json,threading,time,math,array,paho.mqtt.client as mqtt
pygame.mixer.pre_init(22050,-16,1,512)
pygame.init()
I=pygame.display.Info()
W,H=I.current_w,I.current_h
S=pygame.display.set_mode((W,H),pygame.FULLSCREEN)
B,WH,GR,G,R,BL,YL=(15,15,20),(255,255,255),(45,45,55),(0,255,136),(255,50,100),(0,170,255),(255,215,0)
FL=pygame.font.SysFont("arial",int(W*.11),1)
FM=pygame.font.SysFont("arial",int(W*.055),1)
FS=pygame.font.SysFont("arial",int(W*.04))
PW,PH,BR,WIN_SC=int(W*.28),int(H*.022),int(W*.03),5
C=pygame.time.Clock()

def mk_snd(f,d=.08):
 try:
  n=int(22050*d);buf=array.array('h',[int(12000*math.sin(2*math.pi*f*i/22050)*(1-i/n))for i in range(n)])
  return pygame.mixer.Sound(buffer=buf)
 except:return None

S_HIT,S_PT,S_WIN=mk_snd(520,.06),mk_snd(300,.15),mk_snd(780,.4)
def ply(s):
 if s:
  try:s.play()
  except:pass

class Net:
 def __init__(s,rm,h):
  s.rm,s.h,s.ok,s.ox,s.bx,s.by,s.s1,s.s2=f"pp_eg_{rm}",h,0,.5,.5,.5,0,0
  try:s.c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
  except:s.c=mqtt.Client()
  s.c.on_connect=lambda c,u,f,rc:(setattr(s,'ok',1),c.subscribe(f"{s.rm}/{'g'if h else'h'}"))
  s.c.on_message=s.msg
  threading.Thread(target=s.run,daemon=1).start()
 def run(s):
  try:s.c.connect("://hivemq.com",1883,60);s.c.loop_forever()
  except:pass
 def msg(s,c,u,m):
  try:
   d=json.loads(m.payload.decode());s.ox=d.get("x",.5)
   if not s.h:s.bx,s.by,s.s1,s.s2=d.get("bx",.5),d.get("by",.5),d.get("s1",0),d.get("s2",0)
  except:pass
 def sh(s,x,bx,by,s1,s2):
  if s.ok:s.c.publish(f"{s.rm}/h",json.dumps({"x":round(x,3),"bx":round(bx,3),"by":round(by,3),"s1":s1,"s2":s2}))
 def sg(s,x):
  if s.ok:s.c.publish(f"{s.rm}/g",json.dumps({"x":round(x,3)}))
 def cl(s):
  try:s.c.disconnect()
  except:pass

def btn(t,y,c):
 r=pygame.Rect(int(W*.1),y,int(W*.8),int(H*.08))
 pygame.draw.rect(S,c,r,border_radius=15)
 tx=FM.render(t,1,B);S.blit(tx,tx.get_rect(center=r.center));return r

def win_scr(txt,col):
 ply(S_WIN)
 while 1:
  S.fill(B)
  t1=FL.render(txt,1,col);S.blit(t1,t1.get_rect(center=(W//2,H*.32)))
  t2=FM.render(f"First to {WIN_SC} points!",1,WH);S.blit(t2,t2.get_rect(center=(W//2,H*.43)))
  ba,bm=btn("Play Again",int(H*.56),G),btn("Main Menu",int(H*.68),GR)
  pygame.display.flip()
  for e in pygame.event.get():
   if e.type==pygame.QUIT:pygame.quit();sys.exit()
   if e.type==pygame.MOUSEBUTTONDOWN:
    if ba.collidepoint(e.pos):return 1
    if bm.collidepoint(e.pos):return 0

def local(m):
 while 1:
  p1,p2=pygame.Rect(W//2-PW//2,H-int(H*.08),PW,PH),pygame.Rect(W//2-PW//2,int(H*.06),PW,PH)
  bx,by,bs=W//2,H//2,W*.015;sp=bs;dx,dy=random.choice([-1,1])*sp*.6,random.choice([-1,1])*sp
  s1,s2,bk,tc=0,0,pygame.Rect(15,H//2-22,85,44),{}
  while 1:
   S.fill(B);pygame.draw.line(S,GR,(0,H//2),(W,H//2),4)
   for sc,yp in[(s2,H//2-80),(s1,H//2+80)]:st=FL.render(str(sc),1,(65,65,75));S.blit(st,st.get_rect(center=(W//2,yp)))
   pygame.draw.rect(S,GR,bk,border_radius=8);bt=FS.render("Menu",1,WH);S.blit(bt,bt.get_rect(center=bk.center))
   for e in pygame.event.get():
    if e.type==pygame.QUIT:pygame.quit();sys.exit()
    elif e.type in(pygame.FINGERDOWN,pygame.FINGERMOTION):
     tx,ty=e.x*W,e.y*H;tc[e.finger_id]=(tx,ty)
     if e.type==pygame.FINGERDOWN and bk.collidepoint((tx,ty)):return
    elif e.type==pygame.FINGERUP:tc.pop(e.finger_id,None)
    elif e.type==pygame.MOUSEMOTION and any(pygame.mouse.get_pressed()):
     if e.pos[1]>H//2:p1.centerx=e.pos[0]
     elif m=="2p":p2.centerx=e.pos[0]
    elif e.type==pygame.MOUSEBUTTONDOWN and bk.collidepoint(e.pos):return
   for tx,ty in tc.values():
    if ty>H//2:p1.centerx=int(tx)
    elif m=="2p":p2.centerx=int(tx)
   if m=="ai":
    if p2.centerx<bx-10:p2.x+=int(bs*.85)
    elif p2.centerx>bx+10:p2.x-=int(bs*.85)
   p1.clamp_ip(S.get_rect());p2.clamp_ip(S.get_rect());bx+=dx;by+=dy
   if bx-BR<=0:bx,dx=BR,-dx;ply(S_HIT)
   elif bx+BR>=W:bx,dx=W-BR,-dx;ply(S_HIT)
   br=pygame.Rect(bx-BR,by-BR,BR*2,BR*2)
   if br.colliderect(p1)and dy>0:sp=min(sp*1.06,bs*2.2);dx=((bx-p1.centerx)/(PW/2))*sp*.9;dy=-sp;ply(S_HIT)
   elif br.colliderect(p2)and dy<0:sp=min(sp*1.06,bs*2.2);dx=((bx-p2.centerx)/(PW/2))*sp*.9;dy=sp;ply(S_HIT)
   if by<0 or by>H:
    ply(S_PT)
    if by<0:s1+=1
    else:s2+=1
    if s1>=WIN_SC:
     if win_scr("PLAYER 1 WINS!"if m=="2p"else"YOU WIN!",YL):break
     else:return
    if s2>=WIN_SC:
     if win_scr("PLAYER 2 WINS!"if m=="2p"else"CPU WINS!",R):break
     else:return
    bx,by,sp=W//2,H//2,bs;dx,dy=random.choice([-1,1])*sp*.6,(sp if by<0 else-sp)
   pygame.draw.rect(S,G,p1,border_radius=10);pygame.draw.rect(S,R,p2,border_radius=10)
   pygame.draw.circle(S,WH,(int(bx),int(by)),BR);pygame.display.flip();C.tick(60)

def online(rm,h):
 n=Net(rm,h)
 while 1:
  mp,op=pygame.Rect(W//2-PW//2,H-int(H*.08),PW,PH),pygame.Rect(W//2-PW//2,int(H*.06),PW,PH)
  bx,by,bs=W//2,H//2,W*.014;sp=bs;dx,dy=random.choice([-1,1])*sp*.6,sp;s1,s2,ls,bk=0,0,0,pygame.Rect(15,H//2-22,85,44)
  if h:n.sh(.5,.5,.5,0,0)
  while 1:
   S.fill(B);pygame.draw.line(S,GR,(0,H//2),(W,H//2),4)
   ss=FS.render(f"Room {rm}: {'Online'if n.ok else'...'}",1,G if n.ok else R);S.blit(ss,(W//2-ss.get_width()//2,H//2-18))
   my_sc,op_sc=(s1,s2)if h else(s2,s1)
   for sc,yp in[(op_sc,H//2-80),(my_sc,H//2+80)]:st=FL.render(str(sc),1,(65,65,75));S.blit(st,st.get_rect(center=(W//2,yp)))
   pygame.draw.rect(S,GR,bk,border_radius=8);bt=FS.render("Exit",1,WH);S.blit(bt,bt.get_rect(center=bk.center))
   for e in pygame.event.get():
    if e.type==pygame.QUIT:n.cl();pygame.quit();sys.exit()
    elif e.type in(pygame.FINGERDOWN,pygame.FINGERMOTION):
     tx,ty=e.x*W,e.y*H
     if e.type==pygame.FINGERDOWN and bk.collidepoint((tx,ty)):n.cl();return
     mp.centerx=int(tx)
    elif e.type==pygame.MOUSEMOTION and any(pygame.mouse.get_pressed()):mp.centerx=e.pos[0]
    elif e.type==pygame.MOUSEBUTTONDOWN and bk.collidepoint(e.pos):n.cl();return
   mp.clamp_ip(S.get_rect());op.centerx=int((1-n.ox)*W);op.clamp_ip(S.get_rect())
   if h:
    bx+=dx;by+=dy
    if bx-BR<=0:bx,dx=BR,-dx;ply(S_HIT)
    elif bx+BR>=W:bx,dx=W-BR,-dx;ply(S_HIT)
    br=pygame.Rect(bx-BR,by-BR,BR*2,BR*2)
    if br.colliderect(mp)and dy>0:sp=min(sp*1.05,bs*2);dx=((bx-mp.centerx)/(PW/2))*sp*.9;dy=-sp;ply(S_HIT)
    elif br.colliderect(op)and dy<0:sp=min(sp*1.05,bs*2);dx=((bx-op.centerx)/(PW/2))*sp*.9;dy=sp;ply(S_HIT)
    if by<0 or by>H:
     ply(S_PT)
     if by<0:s1+=1
     else:s2+=1
     bx,by,sp=W//2,H//2,bs;dx,dy=random.choice([-1,1])*sp*.6,(sp if by<0 else-sp)
    if time.time()-ls>.033:n.sh(mp.centerx/W,bx/W,by/H,s1,s2);ls=time.time()
   else:
    bx,by,s1,s2=(1-n.bx)*W,(1-n.by)*H,n.s1,n.s2
    if time.time()-ls>.033:n.sg(mp.centerx/W);ls=time.time()
   my_sc,op_sc=(s1,s2)if h else(s2,s1)
   if my_sc>=WIN_SC:
    if win_scr("YOU WIN!",YL):n.s1=n.s2=0;break
    else:n.cl();return
   if op_sc>=WIN_SC:
    if win_scr("YOU LOSE!",R):n.s1=n.s2=0;break
    else:n.cl();return
   pygame.draw.rect(S,G,mp,border_radius=10);pygame.draw.rect(S,R,op,border_radius=10)
   pygame.draw.circle(S,WH,(int(bx),int(by)),BR);pygame.display.flip();C.tick(60)

def rmenu():
 cd,ks="1234",[["1","2","3"],["4","5","6"],["7","8","9"],["C","0","<"]]
 while 1:
  S.fill(B);t=FM.render("Room Code:",1,WH);S.blit(t,t.get_rect(center=(W//2,H*.1)))
  bx=pygame.Rect(W*.2,H*.15,W*.6,H*.08);pygame.draw.rect(S,GR,bx,border_radius=10)
  ct=FL.render(cd,1,G);S.blit(ct,ct.get_rect(center=bx.center))
  kr,bs,gp=[],int(W*.18),int(W*.04);sx=(W-(bs*3+gp*2))//2
  for r,rw in enumerate(ks):
   for c,k in enumerate(rw):
    rc=pygame.Rect(sx+c*(bs+gp),H*.26+r*(bs*.72+gp),bs,int(bs*.68));pygame.draw.rect(S,GR,rc,border_radius=10)
    kt=FM.render(k,1,WH);S.blit(kt,kt.get_rect(center=rc.center));kr.append((rc,k))
  bh,bj,bb=btn("Create (P1)",int(H*.67),G),btn("Join (P2)",int(H*.78),BL),btn("Back",int(H*.89),R);pygame.display.flip()
  for e in pygame.event.get():
   if e.type==pygame.QUIT:pygame.quit();sys.exit()
   if e.type==pygame.MOUSEBUTTONDOWN:
    for rc,k in kr:
     if rc.collidepoint(e.pos):cd=""if k=="C"else cd[:-1]if k=="<"else cd+k if len(cd)<6 else cd
    if cd:
     if bh.collidepoint(e.pos):online(cd,1)
     elif bj.collidepoint(e.pos):online(cd,0)
    if bb.collidepoint(e.pos):return

while 1:
 S.fill(B);t=FL.render("PING PONG",1,G);S.blit(t,t.get_rect(center=(W//2,H*.22)))
 b1,b2,b3,b4=btn("VS Computer",int(H*.42),G),btn("2 Players (1 Phone)",int(H*.54),R),btn("Online (2 Phones)",int(H*.66),BL),btn("Exit",int(H*.78),GR)
 pygame.display.flip()
 for e in pygame.event.get():
  if e.type==pygame.QUIT:pygame.quit();sys.exit()
  if e.type==pygame.MOUSEBUTTONDOWN:
   if b1.collidepoint(e.pos):local("ai")
   elif b2.collidepoint(e.pos):local("2p")
   elif b3.collidepoint(e.pos):rmenu()
   elif b4.collidepoint(e.pos):pygame.quit();sys.exit()
  