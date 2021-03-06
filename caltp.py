#coding=utf-8
import numpy as np
import tifffile as tiff
import crf_c as crf
import cv2
import calF2

FILE_biaozhu = '/home/lenovo/2Tdisk/Wkyao/_/biaozhu_1110.tif'    #fusai标注文件
label = tiff.imread(FILE_biaozhu)
img_file1 = '/home/lenovo/2Tdisk/Wkyao/_/2017/vgg/vgg_1111_4.tif'
img1 = tiff.imread(img_file1)
img_file2 = '/home/lenovo/2Tdisk/Wkyao/_/2017/vgg/vgg_1111_3.tif'
img2 = tiff.imread(img_file2)

FILE_new_2017 = '/home/lenovo/2Tdisk/Wkyao/_/20171105_quarterfinals/quarterfinals_2017.tif'
new_2017 = tiff.imread(FILE_new_2017).transpose([1, 2, 0])
img17_1 = new_2017[:, :, 2]
img17_2 = new_2017[:, :, 3]
img17 = (img17_1 + img17_2) / 2
# 3 4 通道融合.

# F1 = calF2.caltp(label, img1)
# F2 = calF2.caltp(label, img2)
F1 = 632584
F2 = 558045
w1 = float(F1) / (F1 + F2)
w2 = float(F2) / (F1 + F2)
print (w1, w2)


vgg_3_npy = '/home/lenovo/2Tdisk/Wkyao/_/2017/vgg/softmax_vgg_1111_3.npy'
vgg_4_npy = '/home/lenovo/2Tdisk/Wkyao/_/2017/vgg/softmax_vgg_1111_4.npy'

vggnpy3 = np.load(vgg_3_npy)
vggnpy4 = np.load(vgg_4_npy)


def open_and_close(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    # 闭运算
    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # 开运算
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # 膨胀
    img = cv2.dilate(img, kernel)
    return  img


mergesoftmax = w1 * vggnpy3 + w2 * vggnpy4
np.save('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/1111merge.npy', mergesoftmax)
merge = np.argmax(mergesoftmax, 0).astype(np.uint8)
tiff.imsave('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/1111merge.tif', merge)

softmax_merge = np.load('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/1111merge.npy')
merge_list = []
im_2017_list = []
for i in range(25):
    m = softmax_merge[:, :, i * 600:i * 600 + 600]
    merge_list.append(m)
    b = img17[:, i * 600:i * 600 + 600]
    b = np.array([np.array([b for i in range(3)])])
    b = b.transpose(0, 2, 3, 1)
    im_2017_list.append(b)
merge_list.append(softmax_merge[:, :, 15000:15106])
im_2017_list.append(
    np.array([np.array([img17[:, 15000:15106] for i in range(3)])]).transpose(0, 2, 3, 1))

allImg_crf = []
allImg_soft = []

for n, im_2017_part in enumerate(im_2017_list):
# 使用crf:
    soft = merge_list[n]
    im_2017_mean = np.mean(im_2017_list[n], axis=0)
    c = crf.crf(im_2017_mean, soft)
    allImg_crf.append(c)  # 保存整张crf图.
    Crf = np.concatenate(tuple(allImg_crf), axis=1)
#tiff.imsave('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/crf_merge_1108.tif', Crf)
img = open_and_close(Crf)    #膨胀操作
tiff.imsave('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/tp_vggmerge_1111.tif', img)
merge_img = tiff.imread('/home/lenovo/2Tdisk/Wkyao/_/2017/merge/tp_vggmerge_1111.tif')
F1_merge = calF2.caltp(label, merge_img)
print (F1, F2, F1_merge)
























































