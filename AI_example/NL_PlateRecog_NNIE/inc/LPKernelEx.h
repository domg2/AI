/**********************************************************************
文件名：LPKernelEx.h
版本号：Ver3.0	Copyright (C) 2013 - All Rights Reserved
作　者: zp
日	期:	2018.3.4
描　述: 识别库对外接口
**********************************************************************/
#ifndef LPKERNELEX_H_
#define LPKERNELEX_H_
//#include "LPRUtil.h"
#pragma once

#ifndef __linux__
#define LPRAPI __declspec(dllexport)
#else
#define LPRAPI
#endif

#define _NL_COLOR_NAME_MAX (8)
#define _NL_PLATE_NAME_MAX (16)
#define _NL_PATH_LEN (128)

#ifdef __cplusplus
extern "C"
{
#endif
	typedef struct NL_PlateDet_VarOut_t
	{
		char license[_NL_PLATE_NAME_MAX]; // 车牌号码
		char color[_NL_COLOR_NAME_MAX];   // 车牌颜色
		int nTime;						  // 识别所用时间 单位:毫秒
	} NL_PlateDet_VarOut;

	//坐标结构体
	typedef struct LP_RECT_t
	{
		int left;
		int top;
		int right;
		int bottom;
	} LP_RECT;

	// 输入数据结构
	typedef struct NL_PlateDet_VarIn_t
	{
		unsigned char *pubyIm; //图像内存地址
		int dwWidth;		   //图像宽度
		int dwHeight;		   //图像高度
		int dwChannel;		   //图像通道数
		int dwThredTime;
		LP_RECT djObjRect;

	} NL_PlateDet_VarIn;

	LPRAPI int LPR_InitEx(const char *pbyModelPath);
	LPRAPI int LPR_UnInitEx();

	LPRAPI int LPR_FileEx(void *pvVarIn, void *pvVarOut, int &nRecogNum);

#ifdef __cplusplus
}
#endif
#endif
