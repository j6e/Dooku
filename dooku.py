# Joan García Esquerdo - (2016) LGPL
"""Dooku is a PDF refactoring tool. Reasembles 2x1 and 2x2 slides
PDFs into single slide per page PDFs."""
import shutil
import os
import argparse
from wand.image import Image
from PIL import Image as PILImage
from fpdf import FPDF


def crop4(slides):
    """Perform a crop into a 2x2 slides page."""
    width = slides.width
    height = slides.height
    l_images = []
    l_images.append(slides[172:width // 2, 117:height // 2])
    l_images.append(slides[width // 2:width - 172, 117:height // 2])
    l_images.append(slides[172:width // 2, height // 2:height - 117])
    l_images.append(slides[width // 2:width - 172, height // 2:height - 117])
    return l_images


def crop2(slides):
    """Perform a crop into a 2x1 slides page."""
    width = slides.width
    height = slides.height
    #print(width - 20, height)
    l_images = []
    l_images.append(slides[20:width-20, 20:height // 2])
    l_images.append(slides[20:width-20, height // 2: height - 20])
    return l_images


def crop(slides, type):
    """Function selector for croping."""
    if type == 2:
        return crop2(slides)
    if type == 4:
        return crop4(slides)


def pdfToImg(path, img_path, crop_type):
    """Convert a .pdf to various .png images. """
    imgs = Image(filename=path, resolution=300)
    for i, page in enumerate(imgs.sequence):
        with Image(page) as page_image:
            page_image.alpha_channel = False  # Disable transparency
            images = crop(page_image, crop_type) #croping the slides
            for j, image in zip(range(1, crop_type+1), images):
                sufix = "%s%s.png" % (i + 1, j)
                image.save(filename=img_path + sufix)
                clrs = PILImage.open(img_path + sufix).getcolors()
                if clrs is not None and len(clrs) == 1:  # only one color image
                    os.remove(img_path + sufix)


def imgToPDF(dirname):
    """Reasemble .png images into a new .pdf."""
    images = [img for img in os.listdir(os.path.abspath(dirname))]
    img = Image(filename=os.path.abspath(
        dirname + "/" + images[0]), resolution=300)
    width = img.width
    height = img.height
    pdf = FPDF(unit="pt", format=[width, height])
    for image in images:
        image_path = os.path.abspath(dirname + "/" + image)
        pdf.add_page()
        pdf.image(image_path, 0, 0)
    pdf.output(dirname + "-cropped.pdf", "F")


def main():
    """Action!"""
    parser = argparse.ArgumentParser(
        description="Convert a PDF with n x m slides into a PDF with one slide per page.")
    parser.add_argument("file_name", type=str,
                        help="Single file to convert.", nargs="?")
    parser.add_argument(
        "--all", help="Reshape every PDF file in this directory.", action="store_true")
    parser.add_argument("-crop", type=int, choices="24",
                        help="Crop mode: 2 (2x1) or 4 (2x2).    (Default: 4)", default=4)

    try:
        args = parser.parse_args()
    except TypeError:
        print("Error: -crop has to be 2 or 4.")
        exit()

    if args.all is True:
        filenames = [file for file in os.listdir(
            ".") if ".pdf" in file and "-cropped" not in file]

    else:
        filenames = [args.file_name]

    for file in filenames:
        path = os.path.abspath(file)
        dirname = file.strip(".pdf")
        try:
            os.mkdir(dirname)
        except FileExistsError: #harsh but works :)
            shutil.rmtree(os.path.abspath(dirname))
            os.mkdir(dirname)
        img_path = os.path.abspath(dirname + "/page-")
        pdfToImg(path, img_path, args.crop)
        imgToPDF(dirname)
        shutil.rmtree(os.path.abspath(dirname))

if __name__ == "__main__":
    main()
    