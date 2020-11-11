import numpy as np
import xarray as xr
import xroms
import glob

print('start', flush=True)
y = 2010
path = glob.glob('/d1/shared/TXLA_ROMS/output_20yr_obc/%i/ocean_his_00*.nc' % y)
ds = xroms.open_netcdf(path).sel(ocean_time='%i-08' %y)

print('loaded', flush=True)

msk = (ds.lon_rho>-94.5) * (ds.lon_rho<-89.5) * (ds.h>=10.) * (ds.h<=50.)
msk = msk.load()
msk[165:-1, 440:460]= False
msk[130:160, 300:350]= True
msk[76:83, 490:520]= True

print('msk', flush=True)

layer = -(ds.z_w.isel(s_w=slice(None,-1)) + ds.h - 10)
imx = (layer.rename({'s_w':'s_rho'}).drop('s_rho')/ds.dz)
imx = imx.where(imx>0, 0).where(imx<1, 1)
imx_u = xroms.to_u(imx, ds.xroms.grid)
imx_v = xroms.to_v(imx, ds.xroms.grid)

print(1, flush=True)

qu = (ds.u*ds.dy_u*ds.dz_u*imx_u).sum('s_rho')
qv = (ds.v*ds.dx_v*ds.dz_v*imx_v).sum('s_rho')
nu = ds.xroms.grid.diff(qu, 'X', boundary='extend')
nv = ds.xroms.grid.diff(qv, 'Y', boundary='extend')
w10 = (nu+nv)/ds.dA

do_w = xroms.to_s_w(ds.dye_01, ds.xroms.grid)
do10 = xroms.xisoslice(ds.z_w + ds.h, 10., do_w, 's_w')

wo = (w10*do10)
print('start', flush=True)

do10.where(msk, drop=True).to_netcdf('files/do_10.nc')
print('done do', flush=True)
w10.where(msk, drop=True).to_netcdf('files/w_10.nc')
print('done w', flush=True)
wo.where(msk, drop=True).to_netcdf('files/wo_10.nc')
print('done wo', flush=True)

