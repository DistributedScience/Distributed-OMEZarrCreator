
import os
import argparse
import dask.array as da
from zarr.storage import FSStore
from zarr.hierarchy import open_group

from ome_zarr.dask_utils import resize as da_resize

# Usage: to add a downsampled resolution level (e.g. factor 8) to an image or every image in a Plate:
# python add_downsampling.py /path/to/plate.zarr 8

def open_store(name, mode="a"):
    """
    Create an FSStore instance that supports nested storage of chunks.
    """
    return FSStore(
        name,
        auto_mkdir=True,
        key_separator="/",
        normalize_keys=False,
        mode=mode,
    )

def add_resolution(path_to_zarr, factor):

    store = open_store(path_to_zarr)
    img_root = open_group(store)

    root_attrs = img_root.attrs.asdict()
    # print(root_attrs)
    if "plate" in root_attrs:
        # Go through each Well/field...
        wells = root_attrs["plate"]["wells"]
        # print("wells", wells)
        for well in wells:
            well_path = well["path"]
            w = open_group(store, path = well_path)
            # print("w.attrs", w.attrs.asdict())
            for img in w.attrs["well"]["images"]:
                path_to_img = os.path.join(path_to_zarr, well_path, img["path"])
                add_resolution_to_image(path_to_img, factor)
    else:
        add_resolution_to_image(path_to_zarr, factor)


def add_resolution_to_image(path_to_zarr, factor):
    store = open_store(path_to_zarr)
    img_root = open_group(store)
    img_attrs = img_root.attrs.asdict()

    last_path = img_attrs['multiscales'][0]['datasets'][-1]['path']

    path_to_array = os.path.join(path_to_zarr, last_path)

    # if the last path is a number, increment it for next resolution...
    try:
        new_path = str(int(last_path) + 1)
    except ValueError:
        new_path = str(len(img_attrs['multiscales'][0]['datasets']) + 1)
    # write_path = os.path.join(path_to_zarr, new_path)

    downsample_pyramid_on_disk(store, path_to_array, new_path, factor)

    img_attrs = add_path_to_dataset(img_attrs, new_path, factor)
    img_root.attrs["multiscales"] = img_attrs["multiscales"]


def add_path_to_dataset(img_attrs, path, factor):

    last_dataset = img_attrs['multiscales'][0]['datasets'][-1]

    # "datasets" : [ {
    #   "path" : "0",
    #   "coordinateTransformations" : [ {
    #     "scale" : [ 1.0, 1.0, 1.0, 0.29898804047838085, 0.29898804047838085 ],
    #     "type" : "scale"
    #   } ]
    # } ],

    scale = last_dataset["coordinateTransformations"][0]["scale"]
    new_scale = scale.copy()
    new_scale[-1] = scale[-1] / factor
    new_scale[-2] = scale[-2] / factor

    ds = {
        "path": path,
        "coordinateTransformations": [{
            "type": "scale",
            "scale": new_scale
        }]
    }
    img_attrs['multiscales'][0]['datasets'].append(ds)
    return img_attrs


def downsample_pyramid_on_disk(store, path_to_array, new_path, factor):
    """
    Read array from path, downsample and write to zarr
    """
    dask_image = da.from_zarr(path_to_array)

    # resize in X and Y
    dims = list(dask_image.shape)
    dims[-1] = dims[-1] // factor
    dims[-2] = dims[-2] // factor
    output = da_resize(
        dask_image, tuple(dims), preserve_range=True, anti_aliasing=False
    )

    # write to disk
    da.to_zarr(arr=output, url=store, component=new_path)


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('zarr')
    parser.add_argument('factor', type=int, default="2")

    args = parser.parse_args(args)
    # print(args.zarr, args.factor)
    add_resolution(args.zarr, args.factor)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])