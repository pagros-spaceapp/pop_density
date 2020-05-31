""" i didnt really put much comments, but should be understandable """

import h5py
import rasterio
import numpy as np

err = 1e-10

Affine = rasterio.transform.Affine
with h5py.File('sample.h5','r') as f:
    dbn = f['HDFEOS']['GRIDS']['VNP_Grid_DNB']
    attrs = dbn.attrs
    dataset = dbn['Data Fields']

    n, s = attrs['NorthBoundingCoord'][0], attrs['SouthBoundingCoord'][0]
    w, e = attrs['WestBoundingCoord'][0], attrs['EastBoundingCoord'][0]
    dlat, dlon = n-s, e-w
    print(n, s, w, e)

    keys = dataset.keys()
    for key in keys:
        if not key.startswith('BrightnessTemperature'): continue
        grid = dataset[key][:]

        tmp = np.full((1), -1, grid.dtype)
        nodata = tmp[0]

        res = dlat/grid.shape[0], dlon/grid.shape[1]
        assert abs(res[0]-res[1])<err

        transform = Affine.translation(w,s)
        transform *= Affine.scale(res[0])

        # so what i did was to go to the map downloader, select tile by tile
        # then stitch them together to see if it matches, then go qgis check their coords
        grid = grid

        outfile = f'{key}.tif'
        tiff = rasterio.open(
             outfile, 'w',
             driver='GTiff',
             height=grid.shape[0],
             width=grid.shape[1],
             count=1, dtype=grid.dtype,
             crs='+proj=latlong',
             transform=transform,
             nodata=nodata
        )
        tiff.write(grid[:,:], 1)
        tiff.close()
