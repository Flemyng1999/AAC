import os
import time

from osgeo import gdal
import numpy as np
import multiprocessing as mp


def read_tif(file_path):
    # Open the file using gdal
    ds = gdal.Open(file_path)
    if ds is None:
        print(file_path + "file can't open")
        return

    # Get the image size
    width = ds.RasterXSize
    height = ds.RasterYSize

    # Read the data into numpy arrays
    data_ = ds.ReadAsArray(0, 0, width, height)

    # Get the geotransform and projection information
    geotransform_ = ds.GetGeoTransform()
    projection_ = ds.GetProjection()

    # Close the gdal dataset
    del ds

    return data_, geotransform_, projection_


def write_tif(file_path, data_, geotransform_, projection_):
    # set dtype by its size and range
    min_value = np.min(data_)
    max_value = np.max(data_)

    if min_value >= 0 and 4000 <= max_value < 65535:
        output_dtype = gdal.GDT_UInt16
    elif -32768 < min_value <= -4000 and max_value < 32767:
        output_dtype = gdal.GDT_Int16
    else:
        output_dtype = gdal.GDT_Float32

    # Create the output file using gdal
    driver = gdal.GetDriverByName('GTiff')
    bands, height, width = data_.shape
    ds = driver.Create(file_path, width, height, bands, output_dtype)

    # Set the geotransform and projection information
    ds.SetGeoTransform(geotransform_)
    ds.SetProjection(projection_)

    # Write the data to the output file in parallel
    num_cores = mp.cpu_count()
    pool = mp.Pool(num_cores)
    for i in range(bands):
        pool.apply_async(write_band, args=(ds, data_[i], i + 1))
    pool.close()
    pool.join()

    # Close the gdal dataset
    del data_, ds, driver


def write_band(ds, band_data, band_index):
    # Write the data for a single band to the output file
    band = ds.GetRasterBand(band_index)
    band.WriteArray(band_data)
    band.FlushCache()


if __name__ == "__main__":
    # Example usage
    dir_path = r"D:\2022_7_5_sunny"
    input_file = os.path.join(dir_path, "4rad", "rad.bip")
    output_file = os.path.join(dir_path, "4rad", "rad_readwrite_demo.bip")

    s_t = time.time()
    data, geotransform, projection = read_tif(input_file)
    e_t = time.time()
    print("Read tif took {} seconds".format(e_t - s_t))

    s_t = time.time()
    write_tif(output_file, data, geotransform, projection)
    e_t = time.time()
    print("Write tif took {} seconds".format(e_t - s_t))
