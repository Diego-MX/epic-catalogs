
import uvicorn

from .start import app
from . import debug_mode

if debug_mode:
    uvicorn.run('__main__:app', port=80, host='0.0.0.0', reload=True)
else:
    uvicorn.run(app, port=80, host='0.0.0.0')
