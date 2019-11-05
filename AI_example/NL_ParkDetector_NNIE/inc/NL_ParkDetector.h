/*************************************************************
Copyright (C), 2017-2020, 新大陆集团创新发展中心.
All rights reserved

FileName: NL_ParkDetector.hpp
Description:
停车位检测接口文档头文件

History:
<author>	  <time>    <version>   <Abstract>
zhup		2019.04.18   1.1.0		接口标准化
*************************************************************/
#ifndef INC_NL_PARKDETECTOR_H_
#define INC_NL_PARKDETECTOR_H_

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
#define _NL_PARK_MAXINUM (64)
#define _NL_PARK_WIDTH (3640)
#define _NL_PARK_HEIGHT (2048)
#define _NL_PARK_CHANNEL (3)
	// handle structure
	typedef struct NLDJ_PD_Handle_t
	{
		void *pvModel;		//memory for models.
		void *pvBuf;		// d memory for each process.
		long long qwBufLen; //the length of shared memory.
	} NLDJ_PD_Handle;

	// 输入数据结构
	typedef struct NLDJ_PD_VarIn_t
	{
		unsigned char *pubyIm; //图像内存地址
		int dwWidth;		   //图像宽度
		int dwHeight;		   //图像高度
		int dwChannel;		   //图像通道数

	} NLDJ_PD_VarIn;

	typedef struct NL_Rect
	{
		int x;
		int y;
		int width;
		int height;
	} NL_Rect;

	typedef struct NLDJ_PD_VarOut_t
	{
		int pdwStatus[_NL_PARK_MAXINUM];	  //每个车位被占用情况，0为空，1占用
		float pfScore[_NL_PARK_MAXINUM];	  //车位被占用的置信度
		NL_Rect pdjPositon[_NL_PARK_MAXINUM]; //车位位置 top left width height
		int parkNum;						  //车位个数
	} NLDJ_PD_VarOut;

	/**
* Description: 加载模型，只需要在程序最开始执行一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* ------ pbyModelPath			包含模型文件的文件夹路径
* Output:
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	DLLEXPORT int NL_PD_Command(void *pvHandle, char *pbyRootPath); // __declspec(dllexport)

	/**
* Description: 计算车位检测程序所需要的内存大小，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0					    成功
*        <0					失败
*/

	int NL_PD_CalMemSz(void *pvHandle);

	/**
* Description: 初始化内存，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0					    成功
*        <0					失败
*/
	DLLEXPORT int NL_PD_Init(void *pvHandle);

	/**
* Description: 主处理函数，每批(张)图片调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* ------ pvVarIn				车位检测数据结构指针
* Output:
* ------ pvVarOut				车位检测输出数据结构
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	DLLEXPORT int NL_PD_Process(void *pvHandle, void *pvVarIn, void *pvVarOut);

	/**
* Description: 释放句柄中的共享内存，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	int NL_PD_Exit(void *pvHandle);

	/**
* Description: 释放模型所占空间，调用一次
* Input:
* ------ pdjHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	DLLEXPORT int NL_PD_UnloadModel(void *pvHandle);

#ifdef __cplusplus
}
#endif
#endif /** INC_NL_FACEDETECTION_H_ */
