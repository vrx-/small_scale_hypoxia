import xroms

y = 2010
path = '/d1/shared/TXLA_ROMS/output_20yr_obc/%i/ocean_his_00*.nc' % y
ds = xroms.open_roms_netcdf_dataset(path).sel(ocean_time='%i-08' %y)
ds, grid = xroms.roms_dataset(ds, Vtransform=None)

msk = (ds.lon_rho>-94.5) * (ds.lon_rho<-89.5) * (ds.h>=10.) * (ds.h<=50.)
msk = msk.load()
msk[165:-1, 440:460] = False
msk[130:160, 300:350] = True
msk[76:83, 490:520] = True

h = ds.h.where(msk, drop=True)
# rho_depths = ds.z_rho.where(msk, drop=True)
# do = ds.dye_01.where(msk, drop=True)
# print("vars for ldo", flush=True)
# ldo_thk = (h + rho_depths.where(do<=60).max('s_rho')).squeeze()
# print("saving ldo", flush=True)
# ldo_thk.to_netcdf('files/ldo_2010_08.nc')
# print("ldo done", flush=True)

rho = xroms.density(ds.temp, ds.salt, ds.z_rho)
drhodz = grid.derivative(rho, 'Z', boundary='extend').where(msk, drop=True)
w_depths = ds.z_w.where(msk, drop=True)
vcrit = .1
depth_grad = w_depths.where(abs(drhodz)>=vcrit).isel(s_w=slice(1,-1))
print("vars for bbl", flush=True)
bbl = (h + depth_grad.min('s_w')).squeeze()
print("ready", flush=True)
bbl = bbl.to_netcdf('files/bbl_2010_08_v2.nc')
print("done", flush=True)