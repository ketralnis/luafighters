#include <Python.h>

static PyObject* say_hello(PyObject* self, PyObject* args);
PyMODINIT_FUNC inithelloc(void);

static PyMethodDef HelloMethods[] =
{
     {"say_hello", say_hello, METH_VARARGS, "Greet somebody through Lua through C."},
     {NULL, NULL, 0, NULL}
};


