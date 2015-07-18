#include <stdlib.h>
#include <stdio.h>

#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include <Python.h>

#include "hellocmodule.h"

struct custom_alloc_data {
    size_t limit;
    size_t used;
};

void* l_alloc_restricted (void *ud, void *ptr, size_t osize, size_t nsize) {
   struct custom_alloc_data* alloc_data = (struct custom_alloc_data*)ud;

    if (nsize == 0) {
        free(ptr);
        alloc_data->used -= osize; /* subtract old size from used memory */
        return NULL;
    }

    if (alloc_data->used + (nsize - osize) > alloc_data->limit) {
        /* too much memory in use */
        return NULL;
    }

    ptr = realloc(ptr, nsize);
    if (ptr) {
        /* reallocation successful */
        alloc_data->used += (nsize - osize);
    }

    return ptr;
}


static PyObject* say_hello(PyObject* self, PyObject* args) {
    double sum;

    struct custom_alloc_data alloc_data = {102400, 0};

    /*
     * All Lua contexts are held in this structure. We work with it almost
     * all the time.
     */
    lua_State *L = lua_newstate(l_alloc_restricted, &alloc_data);

    /* Load Lua libraries */
    // luaL_openlibs(L); // we don't load any for now

    /* Load the file containing the script we are going to run */
    int status = luaL_loadfile(L, "./luafighters/lua/hellolua.lua");
    if (status) {
        /*
         * If something went wrong, error message is at the top of the stack
         */

        /* copy the errstring out */
        PyObject* pyerrstring = PyString_FromStringAndSize(lua_tostring(L, -1),
                                                           lua_rawlen(L, -1));
         if(!pyerrstring) {
            goto done;
        }

        PyErr_SetObject(PyExc_RuntimeError, pyerrstring);

        goto done;
    }

    /*
     * Ok, now here we go: We pass data to the lua script on the stack.
     * That is, we first have to prepare Lua's virtual stack the way we
     * want the script to receive it, then ask Lua to run it.
     */
    lua_newtable(L); /* We will pass a table */

    /*
     * To put values into the table, we first push the index, then the
     * value, and then call lua_rawset() with the index of the table in the
     * stack. Let's see why it's -3: In Lua, the value -1 always refers to
     * the top of the stack. When you create the table with lua_newtable(),
     * the table gets pushed into the top of the stack. When you push the
     * index and then the cell value, the stack looks like:
     *
     * <- [stack bottom] -- table, index, value [top]
     *
     * So the -1 will refer to the cell value, thus -3 is used to refer to
     * the table itself. Note that lua_rawset() pops the two last elements
     * of the stack, so that after it has been called, the table is at the
     * top of the stack.
     */
    for(int i = 1; i <= 5; i++) {
        lua_pushnumber(L, i);   /* Push the table index */
        lua_pushnumber(L, i*2); /* Push the cell value */
        lua_rawset(L, -3);      /* Stores the pair in the table */
    }

    /* By what name is the script going to reference our table? */
    lua_setglobal(L, "foo");

    printf("C: executing lua code\n");

    /* Ask Lua to run our little script */
    int result = lua_pcall(L, 0, LUA_MULTRET, 0);
    if(result) {
        /*
         * If something went wrong, error message is at the top of the stack
         */

        /* copy the errstring out */
        PyObject* pyerrstring = PyString_FromStringAndSize(lua_tostring(L, -1),
                                                           lua_rawlen(L, -1));
         if(!pyerrstring) {
            goto done;
        }

        PyErr_SetObject(PyExc_RuntimeError, pyerrstring);

        goto done;
        goto done;
    }

    /* Get the returned value at the top of the stack (index -1) */
    sum = lua_tonumber(L, -1);

    printf("C: Script returned: %.0f\n", sum);

    lua_pop(L, 1);  /* Take the returned value out of the stack */

done:
    lua_close(L); /* Cya, Lua */

    if(PyErr_Occurred()) {
        return NULL;
    }

    return PyFloat_FromDouble(sum);
}

PyMODINIT_FUNC inithelloc(void) {
     (void)Py_InitModule("helloc", HelloMethods);
}
