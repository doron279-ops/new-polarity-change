import bpy, math
from mathutils import Vector, Euler
from pathlib import Path
D=Path(__file__).resolve().parent
b=bpy;s=b.context.scene
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def sample(frame,keys):
 for (a,u),(z,v) in zip(keys,keys[1:]):
  if frame<=z:
   t=ease((frame-a)/(z-a));return [i+(j-i)*t for i,j in zip(u,v)]
 return keys[-1][1]
s.frame_start=1;s.frame_end=336;s.render.fps=24
lid=next(o for o in s.objects if o.name.startswith('Cover |'))
floor=next(o for o in s.objects if o.name.startswith('Studio sweep'))
heads=[s.objects[n] for n in ['Marked terminal','Unmarked terminal']]
fib=sorted([o for o in s.objects if o.name.startswith('Continuous buffered')],key=lambda o:o.name)
shots=[(1,'Closed',(-5,0,0),(40,-58,49),65),(41,'Opening direction',(1,0,0),(6,-17,-62),55),(77,'Release cover',(2,1,2),(24,-55,58),57),(137,'Exchange terminals',(3,1,2),(12,-44,64),57),(263,'Close cover',(2,1,2),(24,-55,58),57),(303,'Reversed polarity',(-4,0,0),(33,58,48),64)]
for k,(frame,label,target,offset,scale) in enumerate(shots):
 cam=s.camera.copy();cam.data=s.camera.data.copy();s.collection.objects.link(cam);cam.name=label+' camera';cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(-Vector(offset)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 marker=s.timeline_markers.new(label,frame=frame);marker.camera=cam
 floor.hide_render=frame==41;floor.keyframe_insert(data_path='hide_render',frame=frame)
 if k==0:s.camera=cam
for frame in range(1,337):
 s.frame_set(frame)
 lid.rotation_euler.x=math.radians(sample(frame,[(1,[0]),(84,[0]),(130,[-100]),(266,[-100]),(298,[0])])[0]);lid.keyframe_insert(data_path='rotation_euler',frame=frame)
 for i,h in enumerate(heads):
  sign=2*i-1;base=3.12*sign
  # Lift at different heights before crossing, then lower into the opposite tracks.
  u,z,yaw,pitch=sample(frame,[(1,[0,0,0,0]),(143,[0,0,0,0]),(174,[0,10.3 if not i else 2.9,sign*11,-8 if not i else -3]),(211,[1,10.3 if not i else 2.9,-sign*9,-8 if not i else -3]),(243,[1,0,0,0])])
  yy=base*(1-2*u);rot=Euler((0,math.radians(pitch),math.radians(yaw)));h.rotation_euler=rot
  pivot=Vector((4.9,0,0));end=Vector((4.9-.20*z,yy,z));h.location=end-rot.to_matrix()@pivot
  for path in ['location','rotation_euler']:h.keyframe_insert(data_path=path,frame=frame)
  coords=[(-6.7,base*.13,0),(-4.9,base*.13+(yy-base*.13)*.22,z*.16+(.32 if not i else -.32)*u),(end.x-2.7,yy*.80,z*.84-.22),end]
  coords=list(map(Vector,coords))
  for k,pt in enumerate(fib[i].data.splines[0].bezier_points):
   pt.handle_left_type=pt.handle_right_type='FREE';pt.co=coords[k]
   direction=(coords[min(3,k+1)]-coords[max(0,k-1)]).normalized() if k<3 else rot.to_matrix()@Vector((1,0,0))
   pt.handle_left=pt.co-direction*(coords[k]-coords[max(0,k-1)]).length/3;pt.handle_right=pt.co+direction*(coords[min(3,k+1)]-coords[k]).length/3
   for prop in ['co','handle_left','handle_right']:pt.keyframe_insert(data_path=prop,frame=frame)
s.frame_set(1);s.render.resolution_x=1440;s.render.resolution_y=960;s.cycles.samples=20;s.render.use_persistent_data=True
s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.filepath='//OM4 polarity change.mp4'
b.context.preferences.filepaths.save_version=0
b.ops.wm.save_as_mainfile(filepath=str(D/'OM4 polarity change.blend'))
# Inspect the midpoint before the full render.
s.frame_set(194);s.render.resolution_percentage=50;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=str(D/'previews'/'09_exchange_midpoint.png');b.ops.render.render(write_still=True)


