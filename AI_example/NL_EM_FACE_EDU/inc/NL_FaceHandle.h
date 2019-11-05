/*************************************************************
 Copyright (C), 2017-2020, 新大陆集团创新发展中心.
 All rights reserved

 FileName: NL_FaceHandle.h
 Description:
 H3559A AI模块相关接口

 History:
 <author>  <time>    <version>   <Abstract>
 yuzf    2019-01-15    0.1.0     3559A AI模块接口第一版
 yuzf    2019-01-30    1.0.0     增加人脸优选
 yuzf    2019-02-21    1.1.0     提升最大人脸数_NL_MAXFACENUM 200
 yuzf    2019-02-21    1.2.0     增加时间戳
 yuzf    2019-04-27    1.3.0     修改部分结构体成员
 yuzf    2019-04-30    1.4.0     增加usrdata  
 yuzf    2019-04-30    1.5.0     修改usrdata为std::vector<unsigned char> buff_v;//jpg编码
 yuzf    2019-09-17    1.7.0     为python调用删除c++部分
 *************************************************************/
#ifndef _NL_HANDLE_H_
#define _NL_HANDLE_H_

#ifndef __linux__
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
#ifdef __cplusplus
extern "C"
{
#endif

#define _NL_MAXFACENUM    (255)
#define _NL_FEATURELEN    (512)

#pragma pack(1)

typedef struct FaceRect
{
    float               x1;
    float               y1;
    float               x2;
    float               y2;
    float               score;     /**< Larger score should mean higher confidence. */
} FaceRect;

typedef struct FacePts
{
    float               x[5], y[5];
} FacePts;

typedef struct FaceInfo
{
    FaceRect            bbox;//face box
    float               regression[4];//regress value
    FacePts             facePts;//landmark
    float               quality=1.f;//quality value
    bool                good=true;//Whether to pass quality inspection
    bool                track=false;//Whether to track the ID
    int                 chn;//video channel
    int                 dev;//video device
    unsigned char       *src;//The image address where the face is located
    int                 img_w;//image width
    int                 img_h;//image height
} FaceInfo;

// handle structure
typedef struct NLDJ_EM_Handle_t
{
    void                *fdModel=NULL; //face detect and ext models.
    void                *faModel=NULL; //face align
    int                 fd_nnie_id;//face detect kernel
    int                 fe_nnie_id;//feature ext kernel
} NLDJ_EM_Handle;

// 人脸检测输入数据结构
// 数组第一维度为一帧图片地址，第二维度为金字塔第一层地址，第三维度为时间戳
typedef struct NLDJ_ED_VarIn_t
{
    void*               imgaddr;// source image memory address
    int                 imgWidth;// source image width
    int                 imgHeight;// source image height
    void*               pyramid;//pyramid image memory address
    int                 pydWidth;// pyramid image width
    int                 pydHeight;// pyramid image height
    int                 chn;
    int                 dev;
} NLDJ_ED_VarIn;

// 人脸检测结果输出数据结构
// 数组第一维度为一帧图中所有人脸的信息，第二维度为人脸数，第三维度为时间戳
typedef struct NLDJ_ED_VarOut_t
{
    FaceInfo            faceInfos[_NL_MAXFACENUM];
    unsigned int        num=0; //人脸个数
    int                 chn;
    int                 dev;
} NLDJ_ED_VarOut;

// 对齐输入数据结构
// 数组第一维是图片内存地址(不一定在连续内存上)，对齐成功的人脸数
typedef struct NLDJ_EA_VarIn_t
{
    FaceInfo            faces[_NL_MAXFACENUM];
    unsigned int        num;
}NLDJ_EA_VarIn;

// 对齐输出数据结构
// 数组第一维是图片内存地址(不一定在连续内存上)，对齐成功的人脸数
typedef struct NLDJ_EA_VarOut_t
{
    FaceInfo            faces[_NL_MAXFACENUM];
    unsigned int        num;
}NLDJ_EA_VarOut;

// 特征提取结果输入数据结构
typedef NLDJ_EA_VarOut NLDJ_ER_VarIn;

// 特征提取结果输出数据结构
typedef struct NLDJ_ER_VarOut_t
{
    FaceInfo            faces[_NL_MAXFACENUM];
    float               features[_NL_MAXFACENUM][_NL_FEATURELEN];
    unsigned int        num;
} NLDJ_ER_VarOut;

// 人脸筛选记录结构
typedef struct NLDJ_FACE_t
{
    FaceInfo            faceInfo;
    float               feature[_NL_FEATURELEN]; 
}NLDJ_FACE;

// 人脸筛选输入结构
// 第一维是本次人脸检测结果，第二维是上一帧检测识别结果
// 第三维是上一帧结果数量,第四维度为时间戳
typedef struct NLDJ_ES_VarIn_t
{
    NLDJ_ED_VarOut      *fd_out;
    NLDJ_ER_VarOut      *fr_out;
}NLDJ_ES_VarIn;

// 人脸筛选输出结构
typedef struct NLDJ_ES_VarOut_t
{
    NLDJ_FACE           tracked[_NL_MAXFACENUM];
    unsigned int        trackedNum=0;
    NLDJ_ED_VarOut      untracked;
}NLDJ_ES_VarOut;

#pragma pack()
#ifdef __cplusplus
}
#endif

#endif



