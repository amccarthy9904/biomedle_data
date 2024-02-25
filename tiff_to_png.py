from pathlib import Path
import imageio


def convert_tif_to_png(tif_folder_path, png_folder_path):
    # Convert folder path to a Path object
    tif_folder_path = Path(tif_folder_path)
    png_folder_path = Path(png_folder_path)

    # Iterate through each file in the folder
    for file_path in tif_folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".tif":

            img = imageio.imread(file_path, format='tiff')
    
            new_file_path = png_folder_path.joinpath(f"{file_path.stem}.png")
            imageio.imwrite(new_file_path, img)

            print(f"Converted {file_path.name} to {new_file_path.name}")

if __name__ == "__main__":
    tif_folder_path = input("Enter the .tif folder path: ")
    png_folder_path = input("Enter the .png folder path: ")
    convert_tif_to_png(tif_folder_path, png_folder_path)
