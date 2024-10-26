# %% [markdown]
# # 统计目录下照片的多种信息如焦距、光圈、快门速度等，提供一些趣味以及尽头购买的参考 | Count the focal length, aperture, shutter speed, etc. of the photos in the directory, provide some fun and purchase reference

# %% [markdown]
# ## 导入需要使用的包，指定文件路径和图片类型 | Import the necessary packages and specify the file path and image type to be used

# %%
import pandas as pd  # pip install pyarrow may be suggested
import matplotlib.pyplot as plt
import os
from PIL import Image  # https://pillow.readthedocs.io/en/stable/releasenotes/3.1.0.html
import sys

file_path = "K:\BaiduSyncdisk\Photos"
file_type_a = ".jpg", ".jpeg", ".png"
file_type_A = tuple(map(str.upper, file_type_a))

if not os.path.exists(file_path):
    print("目录不存在")
    sys.exit()

print(file_type_a, file_type_A)

# %% [markdown]
# ## 读取所有目录下的图片文件 | Read all image files in the directory

# %%
# define a list to store the image's file pathes, including the subfolders
jpg_path_list = []
# set
error_path_list = set()
TOTAL_SIZE = 0
for root, dirs, files in os.walk(file_path):
    for file in files:
        if file.endswith(file_type_A) or file.endswith(file_type_a):
            jpg_path_list.append(os.path.join(root, file))
# print the size of the list
TOTAL_SIZE = len(jpg_path_list)
print("The number of the image file is: ", TOTAL_SIZE)
print(jpg_path_list[0:5])

# %% [markdown]
# ## 定义需要使用的方法 | Define the methods to be used
# ``` ref: https://exiv2.org/tags.html ```
# 

# %%
def get_focal_length(image_path):
    """
    Get the focal length of the image.
    :param image_path: the path of the image
    :return: the focal length of the image
    """
    try:
        focal_length = Image.open(image_path)._getexif()[37386]
    except:
        error_path_list.add(image_path)
        PrintErrorImage(image_path)
        return

    return focal_length


def get_F_stop(image_path):
    """
    Get the F-stop of the image.
    :param image_path: the path of the image
    :return: the F-stop of the image
    """
    try:
        F_stop = Image.open(image_path)._getexif()[33437]
    except:
        error_path_list.add(image_path)
        PrintErrorImage(image_path)
        return
    return F_stop


def get_ISO(image_path):
    """
    Get the ISO of the image.
    :param image_path: the path of the image
    :return: the ISO of the image
    """
    try:
        ISO = Image.open(image_path)._getexif()[34855]
    except:
        error_path_list.add(image_path)
        PrintErrorImage(image_path)
        return
    return ISO


def get_shutter_speed(image_path):
    """
    Get the shutter speed of the image.
    :param image_path: the path of the image
    :return: the shutter speed of the image
    """
    try:
        shutter_speed = Image.open(image_path)._getexif()[33434]
    except:
        error_path_list.add(image_path)
        PrintErrorImage(image_path)
        return
    return shutter_speed


import piexif


def get_metadata_piexif(image_path):
    """
    Fetches focal length, F-stop, ISO, and shutter speed of an image in one function call.
    """
    try:
        # 使用 piexif 加载图片的 EXIF 数据
        exif_data = piexif.load(image_path)
        focal_length = exif_data["Exif"].get(37386)  # 焦距
        focal_length = focal_length[0] / focal_length[1]
        F_stop = exif_data["Exif"].get(33437)  # 光圈
        F_stop = F_stop[0] / F_stop[1]
        ISO = exif_data["Exif"].get(34855)  # ISO
        shutter_speed = exif_data["Exif"].get(33434)  # 快门速度
        shutter_speed = shutter_speed[0] / shutter_speed[1]
    except Exception as e:
        error_path_list.add(image_path)
        # PrintErrorImage(image_path)
        return None, None, None, None

    return shutter_speed, ISO, focal_length, F_stop


def get_metadata(image_path):
    """
    Fetches focal length, F-stop, ISO, and shutter speed of an image in one function call.
    """
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        focal_length = exif_data.get(37386)
        F_stop = exif_data.get(33437)
        ISO = exif_data.get(34855)
        shutter_speed = exif_data.get(33434)
    except Exception as e:
        error_path_list.add(image_path)
        PrintErrorImage(image_path)
        # return None, None, None, None
    return shutter_speed, ISO, focal_length, F_stop


def PrintErrorImage(image_path):
    print(
        "Error image: ",
        image_path,
        "may not have focal length, F-stop, ISO, or shutter speed",
    )


def print_progress(progressName, current, total):
    """
    PRINT THE PROGRESS OF THE PROCESS
    :param current: the current number of the process
    :param total: the total number of the process
    """
    progress = current / total
    sys.stdout.write(
        "\r"
        + progressName
        + " Progress: [{0:50s}] {1:.1f}%".format(
            "=" * int(progress * 50), progress * 100
        )
    )
    sys.stdout.flush()

# %% [markdown]
# ## 读取图片信息并存储到pandas的DataFrame中|Read the image information and store it in the pandas DataFrame
# 速度可能较慢，待优化？ | May be slow, to be optimized?

# %%
# shutter_speed_list = []
# ISO_list = []
# focal_length_list = []
# F_stop_list = []
# for jpg_path in jpg_path_list:
#     shutter_speed = get_shutter_speed(jpg_path)
#     ISO = get_ISO(jpg_path)
#     focal_length = get_focal_length(jpg_path)
#     F_stop = get_F_stop(jpg_path)

#     shutter_speed_list.append(shutter_speed)
#     ISO_list.append(ISO)
#     focal_length_list.append(focal_length)
#     F_stop_list.append(F_stop)
#     print_progress("Reading Images", len(shutter_speed_list), len(jpg_path_list))

# %% [markdown]
# ## A much much faster way to read the image information is to use the `piexif` !! Because there is no need to open the image file, just read the exif information directly. | 一个更快的方法是使用`piexif`读取图片信息，因为不需要打开图片文件，直接读取exif信息即可:

# %%
shutter_speed_list = []
ISO_list = []
focal_length_list = []
F_stop_list = []
for jpg_path in jpg_path_list:
    shutter_speed, ISO, focal_length, F_stop = get_metadata_piexif(jpg_path)
    shutter_speed_list.append(shutter_speed)
    ISO_list.append(ISO)
    focal_length_list.append(focal_length)
    F_stop_list.append(F_stop)
    print_progress("Reading Images", len(shutter_speed_list), len(jpg_path_list))

# %% [markdown]
# Alittle bit faster version by using ThreadPoolExecutor:

# %%
data = {
    "shutter_speed(s)": shutter_speed_list,
    "ISO": ISO_list,
    "focal_length(mm)": focal_length_list,
    "F_stop(/f)": F_stop_list,
}
images_df = pd.DataFrame(data, index=jpg_path_list)
images_df
# # save to csv in the same folder
# images_df.to_csv("images_metadata.csv")

# %%
error_images_df = pd.DataFrame(error_path_list, columns=["Error Image Path"])
error_images_df

# %% [markdown]
# ## 搜索目录内图片名称来确保图片是否被正确读取 | Search the directory for image names to ensure that the images are read correctly
# 

# %%
target_image_path = "IMG_1339.JPG"
for index in images_df.index:
    if index.endswith(target_image_path):
        print(target_image_path + " was found at index: ", index)

# %% [markdown]
# ## 分析图片的焦距（如果你有一个变焦镜头的话） | Analyze the focal length of the image (if you have a zoom lens)

# %%
# 定义一个焦段字典，以焦段为键，以数量为值|define a dictionary to store the focal length as the key and the number as the value
focal_length_dict = {
    "8-15 ": 0,
    "16-24": 0,
    "24-35": 0,
    "35-50": 0,
    "50-70": 0,
    "70-105": 0,
    "105-135": 0,
    "135-200": 0,
    "200-300": 0,
    "300-400": 0,
    "400-600": 0,
    "600-800": 0,
    "800-1200": 0,
    "1200-1600": 0,
    "1600-2000": 0,
}


def count_focal_length(df, dict):
    progress = 0
    invalid_count = 0
    # get all
    for index, row in df.iterrows():
        focal_length = row["focal_length(mm)"]
        if pd.isna(focal_length):
            invalid_count += 1
            progress += 1
            print_progress("Counting F-stop", progress, len(df))
            # print("Invalid focal length", index)
            continue
        if focal_length < 15:
            dict["8-15 "] += 1
        elif focal_length < 25:
            dict["16-24"] += 1
        elif focal_length < 35:
            dict["24-35"] += 1
        elif focal_length < 50:
            dict["35-50"] += 1
        elif focal_length < 70:
            dict["50-70"] += 1
        elif focal_length < 105:
            dict["70-105"] += 1
        elif focal_length < 135:
            dict["105-135"] += 1
        elif focal_length < 200:
            dict["135-200"] += 1
        elif focal_length < 300:
            dict["200-300"] += 1
        elif focal_length < 400:
            dict["300-400"] += 1
        elif focal_length < 600:
            dict["400-600"] += 1
        elif focal_length < 800:
            dict["600-800"] += 1
        elif focal_length < 1200:
            dict["800-1200"] += 1
        elif focal_length < 1600:
            dict["1200-1600"] += 1
        elif focal_length < 2000:
            dict["1600-2000"] += 1
        progress += 1
        print_progress("Counting Focal Length", progress, len(df))
    return invalid_count


invalid_count = count_focal_length(images_df, focal_length_dict)
print(" Invalid focal length count: ", invalid_count)
focal_length_dict

# %%
# 以柱状图的形式展示焦段字典，plot标题为照片总数，y轴为焦段，x轴为照片数量，并在每个柱状图上显示照片数量
plt.figure(figsize=(15, 5))
focal_length_series = pd.Series(focal_length_dict)
focal_length_series.plot(kind="bar", title=str.upper("focal length distribution"))
for x, y in enumerate(focal_length_series):
    plt.text(x, y, "%s" % y, ha="center", va="bottom")
plt.legend(["Total valid number of the image: " + str(TOTAL_SIZE - invalid_count)])
plt.xticks(rotation=0)
plt.xlabel("focal length(mm)")
plt.ylabel("number of the image")
plt.show(block=False)

# %% [markdown]
# 以上统计结果可以一定程度上反映出自己喜欢的焦段（前提是你有一个变焦镜头），可以帮助自己更好的选择镜头。

# %% [markdown]
# ### 汇合常用焦段

# %%
# 自定义一个常用焦距区间dict，以焦距区间为键，以数量为值
focal_length_dict_Normal = {
    "8-24": 0,
    "24-70": 0,
    "70-200": 0,
    "200-600": 0,
    "600-2000": 0,
}
# 遍历先前的焦段字典，将焦段数量累加到常用焦距区间字典中
for key, value in focal_length_dict.items():
    if key == "8-15 " or key == "16-24":
        focal_length_dict_Normal["8-24"] += value
    elif key == "24-35" or key == "35-50" or key == "50-70":
        focal_length_dict_Normal["24-70"] += value
    elif key == "70-105" or key == "105-135" or key == "135-200":
        focal_length_dict_Normal["70-200"] += value
    elif key == "200-300" or key == "300-400" or key == "400-600":
        focal_length_dict_Normal["200-600"] += value
    elif (
        key == "600-800"
        or key == "800-1200"
        or key == "1200-1600"
        or key == "1600-2000"
    ):
        focal_length_dict_Normal["600-2000"] += value
# 以柱状图的形式展示焦距区间字典，plot标题为照片总数，y轴为焦距区间，x轴为照片数量，并在每个柱状图上显示照片数量
plt.figure(figsize=(10, 5))

focal_length_series_custom = pd.Series(focal_length_dict_Normal)
focal_length_series_custom.plot(
    kind="bar", title=str.upper("Normalize focal length analysis")
)
for x, y in enumerate(focal_length_series_custom):
    plt.text(x, y, "%s" % y, ha="center", va="bottom")
plt.xticks(rotation=0)
plt.legend(["Total number of valid image: " + str(TOTAL_SIZE - invalid_count)])
plt.xlabel("focal length(mm)")
plt.ylabel("number of the image")
plt.show(block=False)

# %% [markdown]
# ## 分析图片的光圈

# %%
# 统计光圈值，遍历images_df,获取每张图片的光圈值,如果光圈值不在字典中，则将其添加到字典中
F_stop_dict = {}


def count_F_stop(df, dict):
    progress = 0
    invalid_count = 0
    for index, row in df.iterrows():
        F_stop = row["F_stop(/f)"]
        if pd.isna(F_stop):
            invalid_count += 1
            progress += 1
            print_progress("Counting F-stop", progress, len(df))
            # print("Invalid F-stop", index)
            continue
        if F_stop not in dict:
            dict[F_stop] = 1
        else:
            dict[F_stop] += 1
        progress += 1
        print_progress("Counting F-stop", progress, len(df))
    return dict, invalid_count


invalid_count = count_F_stop(images_df, F_stop_dict)[1]
# 根据F_stop_dict 的键排序，以便于后续画图
F_stop_dict = dict(sorted(F_stop_dict.items()))

# %%
# 以柱状图的形式展示光圈值字典，plot标题为照片总数，y轴为光圈值，x轴为照片数量，并在每个柱状图上显示照片数量
plt.figure(figsize=(15, 5))
F_stop_series = pd.Series(F_stop_dict)
F_stop_series.plot(kind="bar", title=str.upper("F-stop distribution"))
for x, y in enumerate(F_stop_series):
    plt.text(x, y, "%s" % y, ha="center", va="bottom")
plt.xlabel("F-stop(/f)")
plt.ylabel("number of the image")
plt.legend(["Total number of valid image: " + str(TOTAL_SIZE - invalid_count)])
plt.xticks(rotation=0)
plt.show(block=False)

# %% [markdown]
# ## 分析图片的快门速度？

# %%
# To be continued??

# %% [markdown]
# ## 快门速度、光圈、焦距之间的关系？| Relationship between shutter speed, aperture, and focal length?

# %%
# 以光圈值为y轴，快门速度为x轴，绘制散点图; 以光圈值为x轴，ISO值为y轴，绘制散点图; 以焦距为x轴，快门速度为y轴，绘制散点图; 以焦距为x轴，ISO值为y轴，绘制散点图;
# draw the scatter plot of the relationship between F-stop and shutter speed, F-stop and ISO, focal length and shutter speed, focal length and ISO
plt.figure(figsize=(15, 10))
plt.subplot(2, 2, 1)
plt.scatter(F_stop_list, shutter_speed_list)
plt.title("F-stop and shutter speed")
plt.xlabel("F-stop(f)")
plt.ylabel("shutter speed(s)")

plt.subplot(2, 2, 2)
plt.scatter(F_stop_list, ISO_list)
plt.title("F-stop and ISO")
plt.xlabel("F-stop(f)")
plt.ylabel("ISO")
plt.subplot(2, 2, 3)
plt.scatter(focal_length_list, shutter_speed_list)
plt.title("focal length and shutter speed")
plt.xlabel("focal length(mm)")
plt.ylabel("shutter speed(s)")

plt.subplot(2, 2, 4)
plt.scatter(focal_length_list, ISO_list)
plt.title("focal length and ISO")
plt.xlabel("focal length(mm)")
plt.ylabel("ISO")
plt.show(block=False)

# %%
# 以光圈值为x轴，快门速度为y轴，焦距为z轴，ISO值为颜色（值越大透明度越低）绘制3D散点图
# draw the 3D scatter plot of the relationship between F-stop, shutter speed, focal length and ISO

# remove the invalid data
images_df = images_df.dropna()

fig = plt.figure()
# size of the figure
fig.set_size_inches(10, 8)
ax = fig.add_subplot(111, projection="3d")
x = images_df["F_stop(/f)"]
y = images_df["shutter_speed(s)"]
z = images_df["focal_length(mm)"]
c = images_df["ISO"]
img = ax.scatter(x, y, z, c=c, cmap=plt.hot())
fig.colorbar(img)
ax.set_xlabel("F-stop(/f)")
ax.set_ylabel("shutter speed(s)")
ax.set_zlabel("focal length(mm)")
plt.show()
images_df


