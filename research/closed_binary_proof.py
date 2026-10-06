"""Read binary DRUP only after explicitly flushing the native trace buffer.

Search/export utility, not a logical proof checker. Strict parsing rejects
truncated headers, clauses and varints; it never manufactures an empty clause.
Linux file-descriptor duplication keeps the temporary file readable on close.
"""
import os
import ctypes

def parse_binary(raw):
    lines=[];i=0
    while i<len(raw):
        marker=raw[i];i+=1
        if marker not in (97,100):raise ValueError('bad proof record marker')
        row=[]
        while True:
            if i==len(raw):raise ValueError('truncated clause')
            if raw[i]==0:i+=1;break
            v=0;shift=0
            while True:
                if i==len(raw):raise ValueError('truncated varint')
                byte=raw[i];i+=1;v|=(byte&127)<<shift;shift+=7
                if shift>63:raise ValueError('oversize literal')
                if byte<128:break
            if v<2:raise ValueError('zero variable')
            row.append(-(v//2) if v&1 else v//2)
        lines.append(('d ' if marker==100 else '')+' '.join(map(str,row))+(' ' if row else '')+'0')
    return lines

def close_and_read(solver):
    """Use the pinned CaDiCaL 1.9.5 C++ API; fail closed if unavailable.

    This is an untrusted exporter using the existing python-sat native object,
    not part of the standard-library proof verifier. Ordinary fflush(NULL)
    is insufficient for CaDiCaL's internal trace buffer.
    """
    import pysolvers
    import pysat
    if pysat.__version__!='1.9.dev15' or type(solver.solver).__name__!='Cadical195':
        raise RuntimeError('native export adapter requires python-sat 1.9.dev15/CaDiCaL195')
    native=solver.solver
    if native.prfile is None:raise ValueError('proof not enabled')
    fd=os.dup(native.prfile.fileno())
    try:
        before=os.fstat(fd).st_size
        prefix=os.pread(fd,before,0)
        library=ctypes.CDLL(pysolvers.__file__)
        flush=getattr(library,'_ZN10CaDiCaL1956Solver17flush_proof_traceEb')
        flush.argtypes=[ctypes.c_void_p,ctypes.c_bool];flush.restype=None
        pointer=ctypes.pythonapi.PyCapsule_GetPointer
        pointer.argtypes=[ctypes.py_object,ctypes.c_char_p];pointer.restype=ctypes.c_void_p
        flush(pointer(native.cadical,None),False)
        length=os.fstat(fd).st_size
        raw=os.pread(fd,length,0)
        if len(raw)!=length:raise OSError('short proof read')
        lines=parse_binary(raw)
        solver.delete()
        final_length=os.fstat(fd).st_size
        final_raw=os.pread(fd,final_length,0)
        if len(final_raw)!=final_length or not final_raw.startswith(raw):
            raise RuntimeError('trace replaced or unreadable on teardown')
        # Destruction can append deletion records; they are not part of the
        # explicitly flushed proof snapshot. The logical checker validates it.
        return lines,dict(bytes_before_native_flush=before,bytes_after_native_flush=length,
                          bytes_after_teardown=final_length,teardown_parse_complete=_complete(final_raw),
                          prefix_unchanged=raw.startswith(prefix),
                          before_parse_complete=_complete(prefix),after_parse_complete=True)
    finally:os.close(fd)

def _complete(raw):
    try:parse_binary(raw);return True
    except ValueError:return False
