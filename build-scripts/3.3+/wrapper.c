#include <stdlib.h>
void AStyleErrorHandler(int errorNumber, const char* errorMessage);
char* AStyleMain(const char* pSourceIn, const char* pOptions, void (*fpError)(int, const char*), void* (*fpAlloc)(unsigned long));

char* AStyleWrapper(const char* pSourceIn, const char* pOptions)
{
    return AStyleMain(pSourceIn, pOptions, &AStyleErrorHandler, malloc);
}
