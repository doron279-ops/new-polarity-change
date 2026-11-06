import bpy, math, os
from mathutils import Vector
from math import pi,sin,cos
from pathlib import Path
D=Path(__file__).resolve().parent
P=D/'previews'; P.mkdir(exist_ok=True)
b=bpy; b.ops.wm.read_factory_settings(use_empty=True)
s=b.context.scene
asset=b.data.collections.new('OM4 LC Uniboot');s.collection.children.link(asset);asset.asset_mark()
def mat(n,c,r=.36,metal=0,tr=0):
 m=b.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=tr
 if n=='Sea glass | molded PBT':
  t=m.node_tree.nodes.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=220;u=m.node_tree.nodes.new('ShaderNodeBump');u.inputs['Strength'].default_value=.11;u.inputs['Distance'].default_value=.012;m.node_tree.links.new(t.outputs['Fac'],u.inputs['Height']);m.node_tree.links.new(u.outputs['Normal'],p.inputs['Normal'])
 return m
a=mat('Sea glass | molded PBT',(.087,.40,.356));w=mat('Warm ivory elastomer',(.79,.76,.66),.48);j=mat('Aqua polyurethane',(.035,.40,.34),.4);g=mat('Emerald identification resin',(.019,.205,.012),.23,0,.25);y=mat('Yellow buffer',(.88,.62,.018));f=mat('Opal buffer',(.80,.85,.79),.3,0,.22);metal=mat('Nickel sleeve',(.52,.47,.40),.21,.93);cer=mat('Zirconia',(.88,.87,.84),.19);ground=mat('Studio slate',(.11,.135,.145),.67)
def finish(o,n,m,bev=0):
 o.name=n;o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 asset.objects.link(o)
 if bev:
  mod=o.modifiers.new('Tool edge radius','BEVEL');mod.width=bev;mod.segments=3
  mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL')
 return o
def box(n,loc,dim,m=a,r=.075):
 b.ops.mesh.primitive_cube_add(size=1,location=loc);o=b.context.object;o.dimensions=dim;b.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,m,r)
def mesh(n,v,faces,m,r=.04):
 me=b.data.meshes.new(n);me.from_pydata(v,[],faces);me.update();o=b.data.objects.new(n,me);return finish(o,n,m,r)
def slab(n,outline,z,h):
 N=len(outline);return mesh(n,[(x,y,k) for k in [z,z+h] for x,y in outline],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],a)
def profile(n,pts,m,ang=2*pi,rot=0):
 N=64;v=[(x,r*cos(rot+ang*i/N),r*sin(rot+ang*i/N)) for x,r in pts for i in range(N+1)];faces=[(k*(N+1)+i,k*(N+1)+i+1,(k+1)*(N+1)+i+1,(k+1)*(N+1)+i) for k in range(len(pts)-1) for i in range(N)]
 o=mesh(n,v,faces,m,0)
 for p in o.data.polygons:p.use_smooth=True
 return o
def wire(n,pts,r,m):
 c=b.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=18;c.bevel_depth=r;c.bevel_resolution=4;sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
 return finish(b.data.objects.new(n,c),n,m)
def empty(n,loc):
 o=b.data.objects.new(n,None);asset.objects.link(o);o.location=loc;return o
def attach(o,parent):
 o.parent=parent;o.location-=parent.location
outline=[(-11,-3.7),(-8.2,-6),(9,-6),(9,6),(-8.2,6),(-11,3.7)]
slab('Lower case • chamfered cable throat',outline,-3.05,.72)
for side in [-1,1]:
 slab('Tray perimeter',[(x,side*v) for x,v in [(-11,3.7),(-8.2,6),(9,6),(9,5.37),(-8,5.37),(-11,3.08)]],-2.4,2.5)
 for xx in [-6.6,7.9]:
  box('Channel keeper',(xx,side*4.95,-.64),(1.4,1.3,3.4))
 for yy in [1.02,5.12]:box('Terminal guide land',(6.8,side*yy,-1.65),(4.1,.43,1.4))
slab('Forked guide • pointed divider',[(-2.4,0),(.6,-1.45),(6.9,-1.45),(6.9,-.98),(.8,-.98),(-1.45,0),(.8,.98),(6.9,.98),(6.9,1.45),(.6,1.45)],-2.35,1.25)
lid=empty('Cover | longitudinal hinge', (0,5.78,0))
def L(o):attach(o,lid);return o
L(slab('Opening cover skin',outline,2.38,.66))
for side in [-1,1]:
 L(slab('Cover skirt',[(x,side*v) for x,v in [(-11,3.7),(-8.2,6),(9,6),(9,5.38),(-8,5.38),(-11,3.08)]],.12,2.29))
for x in [-4,3.7]:
 o=profile('Hinge knuckle',[(x-1.6,.1),(x-1.6,.64),(x+1.6,.64),(x+1.6,.1)],a);o.location.y=5.72
for sy in [-1,1]:
 L(box('Side snap tongue',(.4,sy*6,.52),(8.5,.31,1.48),a,.12))
# arched shared trigger extruded across both heads
def ribbon(n,path,width,thick,yy=0):
 v=[(x,yy+off,z+dz) for x,z in path for off,dz in [(-width/2,0),(width/2,0),(width/2,thick),(-width/2,thick)] ];N=len(path);return mesh(n,v,[(0,3,2,1),tuple(range(4*N-4,4*N))]+[(4*k+i,4*k+(i+1)%4,4*k+4+(i+1)%4,4*k+4+i) for k in range(N-1) for i in range(4)],a,.08)
L(ribbon('Common bowed release paddle',[(-2.9,2.96),(-1.5,3.9),(.6,4.72),(3.1,5.36),(5,5.56),(6.8,5.55),(7.3,5.78),(8,5.78),(8.5,5.56),(9.2,5.76),(10.1,5.76)],8.9,.57))
# embossed underside legends face outward
c=b.data.curves.new('Mold lettering','FONT');c.body='OPEN';c.align_x='CENTER';c.align_y='CENTER';c.size=2.35;c.extrude=.055;c.bevel_depth=.019
o=finish(b.data.objects.new('OPEN | molded legend',c),'OPEN | molded legend',a);o.location=(-.5,-1.65,-3.05);o.rotation_euler.x=pi
for pts in [[(-3.7,1.3),(-.5,3),(2.7,1.3),(-3.7,1.3)],[(-3.7,.72),(2.7,.72)]]:
 arrow=wire('Opening direction relief',[(x,y,-3.095) for x,y in pts],.093,a)
 for bp in arrow.data.splines[0].bezier_points:bp.handle_left_type=bp.handle_right_type='VECTOR'
profile('Swaged entry sleeve',[(-11.4,1.75),(-11.4,2.35),(-10.8,2.48),(-10.5,2.28),(-7,2.28),(-6.8,2.55),(-6.25,2.55),(-6.25,1.15)],metal)
profile('Jacket',[(-85,1.48),(-6.6,1.48)],j)
profile('Boot | smooth shoulder',[(-22,1.91),(-21.7,2.22),(-11.5,2.63),(-11.12,2.48),(-11.12,1.54)],w)
for k in range(8):
 x=-22-k*1.92;r=2.22-.077*k
 profile('Flex rib',[(x-1.16,1.48),(x-1.16,r-.04),(x-1.07,r),(x-.09,r),(x,r-.03),(x,1.48)],w)
 for h in [0,pi]:profile('Alternating flex web',[(x-1.92,1.47),(x-1.92,r-.07),(x-1.16,r-.04),(x-1.16,1.47)],w,1.62,h+k*pi/2)
heads=[];fib=[]
for idx,yy in enumerate([-3.12,3.12]):
 head=empty(['Marked terminal','Unmarked terminal'][idx],(0,yy,0));heads.append(head)
 def H(o):attach(o,head)
 H(box('Keyed locking collar',(9.1,yy,0),(3.6,4.48,4.15),[g,a][idx],.18))
 H(box('Collar flange',(7.65,yy,0),(.78,5.05,4.65),[g,a][idx]))
 barrel=box('LC plug barrel',(17.55,yy,0),(13.5,4.48,4.28))
 key=box('Pocket tool',(13.2,yy,.09),(1.12,5,.99),a,0)
 mod=barrel.modifiers.new('Transverse inspection window','BOOLEAN');mod.operation='DIFFERENCE';mod.object=key
 b.context.view_layer.objects.active=barrel;b.ops.object.modifier_apply(modifier=mod.name);b.data.objects.remove(key,do_unlink=True);H(barrel)
 H(box('Nose polarization rail',(18.7,yy+1.87,2.13),(10.95,.69,.65)))
 H(ribbon('Individual spring latch',[(23.65,2.13),(21.3,2.52),(18.5,3.18),(15.4,4.12),(14.4,4.34),(13.6,4.04),(11.65,4.04),(10.75,4.42)],2.72,.48,yy))
 H(box('LC catch shoulder',(14.85,yy,4.12),(1.62,3.72,.65)))
 o=profile('Polished ceramic ferrule',[(24.25,.625),(25.77,.625),(25.94,.53),(25.94,0)],cer);o.location.y=yy;H(o)
 o=profile('Buffer protection tube',[(4.65,.59),(7.55,.68)],f);o.location.y=yy;H(o)
 fib.append(wire('Continuous buffered fiber', [(-6.7,yy*.13,0),(-4.8,yy*.34,-.25),(1.8,yy*.85,-.22),(4.9,yy,0)],.214,[y,f][idx]))
# Studio and cameras
def studio(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 s.collection.objects.link(o)
floor=box('Studio sweep',(0,0,-3.33),(1200,1200,.33),ground);studio(floor)
world=b.data.worlds.new('Soft ambient');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.75,.81,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,size,power in [((12,-35,50),40,41000),((-28,28,35),32,35000),((36,23,20),23,13500)]:
 b.ops.object.light_add(type='AREA',location=loc);o=b.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,0))
b.ops.object.camera_add();cam=b.context.object;s.camera=cam;cam.data.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=14;s.cycles.use_denoising=True
try:
 prefs=b.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 if any(d.type=='OPTIX' for d in prefs.devices):
  for d in prefs.devices:d.use=d.type=='OPTIX'
  s.cycles.device='GPU'
except:pass
s.render.resolution_x=1080;s.render.resolution_y=720;s.render.resolution_percentage=100
def state(opened,swap):
 lid.rotation_euler.x=math.radians(-100 if opened else 0)
 for i,h in enumerate(heads):
  base=(-1 if i==0 else 1)*3.12;end=-base if swap else base;h.location.y=end
  for p,(xx,frac,zz) in zip(fib[i].data.splines[0].bezier_points,[(-6.7,0,0),(-4.8,.34,-.25),(1.8,.85,-.22),(4.9,1,0)]):p.co=(xx,end*frac if frac else base*.13,zz)
def camera(t,v,sc):
 cam.location=Vector(t)+Vector(v);point(cam,t);cam.data.ortho_scale=sc
views=[('01_closed_hero',0,0,(-5,0,0),(40,-58,49),60),('02_closed_opposite',0,0,(-5,0,0),(28,60,29),64),('03_open_mark',0,0,(2,0,0),(9,-20,-60),54),('04_top_front',0,0,(6,0,0),(54,-22,56),49),('05_open_mechanism',1,0,(2,1,1),(27,-49,53),53),('06_open_tracks',1,0,(3,2,0),(0,-3,75),49),('07_polarity_changed',1,1,(3,2,0),(0,-3,75),49),('08_closed_after_swap',0,1,(-5,0,0),(40,-58,49),60)]
def setup(v):
 n,op,sw,t,d,sc=v;state(op,sw);camera(t,d,sc);floor.hide_render=d[2]<0
s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;b.context.preferences.filepaths.save_version=0
setup(views[0]);s.render.filepath='//previews/';b.ops.wm.save_as_mainfile(filepath=str(D/'OM4 Uniboot.blend'))
for v in views:
 setup(v);s.render.filepath=str(P/(v[0]+'.png'));b.ops.render.render(write_still=True)

