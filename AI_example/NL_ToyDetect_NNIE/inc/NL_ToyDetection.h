﻿/*************************************************************
Copyright (C), 2017-2020, 新大陆集团创新发展中心.
All rights reserved

FileName: NL_ToyDetection.hpp
Description:
目标检测接口文档头文件

History:
<author>	  <time>			<version>   <Abstract>
zhup		  2019.08.26    	1.1.0		接口标准化
*************************************************************/
#ifndef INC_NL_TOYDETECTION_H_
#define INC_NL_TOYDETECTION_H_

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
#define _NL_TD_MAXIUM_OBJ (128)
#define _NL_TD_MAX (5)
#define _NL_TD_NAME_MAX (50)
	// handle structure
	typedef struct NLDJ_TD_Handle_t
	{
		void *pvModel;		//memory for models.
		void *pvBuf;		// d memory for each process.
		long long qwBufLen; //the length of shared memory.
	} NLDJ_TD_Handle;

	// 输入数据结构
	typedef struct NLDJ_TD_VarIn_t
	{
		unsigned char *pubyIm; //图像内存地址
		int dwWidth;		   //图像宽度
		int dwHeight;		   //图像高度
		int dwChannel;		   //图像通道数

	} NLDJ_TD_VarIn;

	typedef struct NLDJ_TD_ObjInfor_t
	{
		int dwClassID;
		int dwLeft;
		int dwTop;
		int dwRight;
		int dwBottom;
		float fscore;
		char className[_NL_TD_NAME_MAX];
	} NLDJ_TD_ObjInfor;

	typedef struct NLDJ_TD_VarOut_t
	{
		int dwObjectSize;
		NLDJ_TD_ObjInfor pdjToyInfors[_NL_TD_MAXIUM_OBJ];
	} NLDJ_TD_VarOut;

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
	DLLEXPORT int NL_TD_Command(void *pvHandle, char *pbyRootPath); // __declspec(dllexport)

	/**
* Description: 计算车位检测程序所需要的内存大小，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0					    成功
*        <0					失败
*/
	int NL_TD_CalMemSz(void *pvHandle);

	/**
* Description: 初始化内存，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0					    成功
*        <0					失败
*/
	int NL_TD_Init(void *pvHandle);

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
	DLLEXPORT int NL_TD_Process(void *pvHandle, void *pvVarIn, void *pvVarOut);

	/**
* Description: 释放句柄中的共享内存，调用一次
* Input:
* ------ pvHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	int NL_TD_Exit(void *pvHandle);

	/**
* Description: 释放模型所占空间，调用一次
* Input:
* ------ pdjHandle				车位检测内存分配句柄
* Output:
* Return:
* ------ 0						退出成功
* ------ <0					退出失败(失败类型详见头文件"NL_err.h")
*/
	DLLEXPORT int NL_TD_UnloadModel(void *pvHandle);

#ifdef __cplusplus
}
#endif
#endif /** INC_NL_FACEDETECTION_H_ */
