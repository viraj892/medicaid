for /f %%f in ('dir *.png /b /O:D') do tesseract %%f %%f --psm 6 --oem 2 letters