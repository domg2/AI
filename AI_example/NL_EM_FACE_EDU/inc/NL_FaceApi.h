/*************************************************************
 Copyright (C), 2017-2020, 新大陆集团创新发展中心.
 All rights reserved

 FileName: NL_FaceApi.h
 Description:
 H3559A AI模块相关接口

 History:
 <author>  <time>    <version>   <Abstract>
 yuzf    2019-01-15    0.1.0     3559A AI模块接口第一版
 yuzf    2019-01-16    0.3.0     修改nl_comm.h
 yuzf    2019-01-17    0.5.0     修复Padding中BUG;修复检测输出越界的问题;
 yuzf    2019-01-17    0.6.0     接口增加硬件传入金字塔；速度优化;增加配置文件读取
 yuzf    2019-01-30    1.0.0     年前正式版，模块分离、完成对齐和识别接口、增加对齐和识别的输入输出结构体、优化部分代码。
 yuzf    2019-01-30    1.1.0     增加人脸优选、比对
 yuzf    2019-02-18    1.2.0     分离人脸检测、对齐、识别内存初始化
 yuzf    2019-02-18    1.3.0     优化NMS
 yuzf    2019-02-18    1.4.0     增加最大人脸数_NL_MAXFACENUM 200，优化对齐代码进行并行计算
 yuzf    2019-02-18    1.4.1     修复接口退出的bug
 yuzf    2019-02-18    1.5.0     RNET,ONET预处理部分并行计算
 yuzf    2019-04-09    1.5.1     增加异常处理，配置文件增加其他模块
 yuzf    2019-04-09    1.6.3     修改人脸检测中的GenerateBoundingBox中一帧大小u32FeatureSize * confidence->u32Num，修改为u32FeatureSize * confidence->unShape.stWhc.u32Chn
 yuzf    2019-09-17    1.7.0     为python调用删除c++部分
 *************************************************************/
#ifndef NL_FACEAPI_H_
#define NL_FACEAPI_H_

#ifndef __linux__
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
#ifdef __cplusplus
extern "C"
{
#endif

    /**************** 输入，输出，与句柄结构体定义 ****************/
    /**
 * Description: 加载模型，只需要在程序最开始执行一次
 * Input:
 * ------ pvHandle				分配句柄
 * ------ pbyConfigPath			配置文件路径
 * Output:
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败(失败类型详见头文件"NL_err.h")
 */
    int NL_EM_Command(void *pvHandle, char *pbyConfigPath);

    /**
 * Description: 人脸检测初始化内存，调用一次
 * Input:
 * ------ pvHandle				分配句柄
 * Output:
 * Return:
 * ------ 0					    成功
 *        <0					失败
 */
    int NL_ED_Init(void *pvHandle);

    /**
 * Description: 人脸对齐初始化内存，调用一次
 * Input:
 * ------ pvHandle				分配句柄
 * Output:
 * Return:
 * ------ 0					    成功
 *        <0					失败
 */
    int NL_EA_Init(void *pvHandle);

    /**
 * Description: 人脸识别初始化内存，调用一次
 * Input:
 * ------ pvHandle				分配句柄
 * Output:
 * Return:
 * ------ 0					    成功
 *        <0					失败
 */
    int NL_ER_Init(void *pvHandle);

    /**
 * Description: 人脸检测主处理函数，每张图片调用一次
 * Input:
 * ------ pvHandle				句柄
 * ------ pvVarIn				输入结构体
 * Output:
 * ------ pvVarOut				人脸检测输出数据结构
 * Return:
 * ------ 0						成功
 * ------ <0					失败
 */
    int NL_ED_Process(void *pvHandle, void *pvVarIn, void *pvVarOut);

    /**
 * Description: 人脸筛选主处理函数
 * Input:
 * ------ pvHandle				句柄
 * ------ pvVarOut				人脸检测输出数据结构
 * Output:
 * ------ pvVarOut				人脸检测输出数据结构
 * Return:
 * ------ 0						成功
 * ------ <0					失败
 */
    int NL_ES_Process(void *pvHandle, void *pvVarIn, void *pvVarOut);

    /**
 * Description: 对齐主处理函数，每张脸调用一次
 * Input:
 * ------ pvHandle				句柄
 * ------ faVarIn				对齐输入结构体
 * Output:
 * ------ align_pkg				齐后的CPU内存地址
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败
 */
    int NL_EA_Process(void *pvHandle, void *faVarIn, void *faVarOut);

    /**
 * Description: 特征提取主处理函数，每张图片调用一次
 * Input:
 * ------ pvHandle				句柄
 * ------ pvVarIn				特征提取输入数据结构
 * Output:
 * ------ pvVarOut				特征提取输出数据结构
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败
 */
    int NL_ER_Process(void *pvHandle, void *feVarIn, void *feVarOut);

    /**
 * Description: 特征比对主要处理函数
 * Input:
 * ------ fea1				    特征
 * ------ fea2				    特征
 * Output:
 * ------ dis				    相似度
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败
 */
    int NL_EC_Process(float fea1[], float fea2[], float &dis);

    /**
 * Description: 释放句柄中的共享内存，调用一次
 * Input:
 * ------ pvHandle				句柄
 * Output:
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败(失败类型详见头文件"NL_err.h")
 */
    int NL_EM_Exit(void *pvHandle);

    /**
 * Description: 释放模型所占空间，调用一次
 * Input:
 * ------ pdjHandle				句柄
 * Output:
 * Return:
 * ------ 0						退出成功
 * ------ <0					退出失败(失败类型详见头文件"NL_err.h")
 */
    int NL_EM_UnloadModel(void *pvHandle);
#ifdef __cplusplus
}
#endif

#endif /* NL_FACEAPI_H_ */
