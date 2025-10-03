# Imports
import numpy as np
from skimage import io as skio
from skimage import transform
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader
import io
import math

# Functions
inch_to_cm = lambda x: x*2.54
def tile_image_pdf(image:np.ndarray, poster_hw:tuple[float], paper_hw:tuple[float], margin:float=0.2, units:str='in') -> None:
    assert units in ['in', 'cm'], f'Error, supported units: [in, cm], got {units}'
    assert len(poster_hw) == 2
    assert len(paper_hw) == 2

    if units == 'cm': 
        poster_hw = [inch_to_cm(item) for item in poster_hw]
        paper_hw = [inch_to_cm(item) for item in paper_hw]
        margin = inch_to_cm(margin)

    image_shape = image.shape
    poster_shape = (poster_hw[0], poster_hw[1], image_shape[-1])
    ar_image = image_shape[0] / image_shape[1]
    ar_poster = poster_shape[0] / poster_shape[1]

    if (ar_image - ar_poster) > 1e-3: 
        print(ar_image, ar_poster)
        print('Warning, aspect ratio specified differs from original image aspect ratio, image will be stretched')

    poster_hwc_px = [int(item * 72) for item in poster_hw] + [image_shape[-1]]
    image = transform.resize(image, poster_hwc_px, preserve_range=True).astype(np.uint8)

    papers_shape = [math.ceil(i1/(i2-2*margin)) for i1, i2 in zip(poster_hw, paper_hw)]
    step_h, step_w = [int((item - 2*margin)*72) for item in paper_hw]

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=[item * 72 for item in paper_hw][::-1])

    for i in range(papers_shape[0]): 
        for j in range(papers_shape[1]):
            image_chunk = image[i*step_h:(i+1)*step_h, j*step_w:(j+1)*step_w,...]
            if 0 not in image_chunk.shape:
                img_buffer = io.BytesIO()
                skio.imsave(img_buffer, image_chunk, format='png')
                img_buffer.seek(0)

                c.drawImage(ImageReader(img_buffer), margin*72, margin*72)
                c.showPage()

    c.save()
    return pdf_buffer

