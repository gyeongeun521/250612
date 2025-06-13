UnicodeDecodeError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/250612/main.py", line 18, in <module>
    df = load_data()
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 219, in __call__
    return self._get_or_create_cached_value(args, kwargs, spinner_message)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 261, in _get_or_create_cached_value
    return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 320, in _handle_cache_miss
    computed_value = self._info.func(*func_args, **func_kwargs)
File "/mount/src/250612/main.py", line 11, in load_data
    df = pd.read_csv("서울시 공중화장실 위치정보.csv")
         ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 1026, in read_csv
    return _read(filepath_or_buffer, kwds)
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 620, in _read
    parser = TextFileReader(filepath_or_buffer, **kwds)
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 1620, in __init__
    self._engine = self._make_engine(f, self.engine)
                   ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/parsers/readers.py", line 1898, in _make_engine
    return mapping[engine](f, **self.options)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/pandas/io/parsers/c_parser_wrapper.py", line 93, in __init__
    self._reader = parsers.TextReader(src, **kwds)
                   ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
File "pandas/_libs/parsers.pyx", line 574, in pandas._libs.parsers.TextReader.__cinit__
File "pandas/_libs/parsers.pyx", line 663, in pandas._libs.parsers.TextReader._get_header
File "pandas/_libs/parsers.pyx", line 874, in pandas._libs.parsers.TextReader._tokenize_rows
File "pandas/_libs/parsers.pyx", line 891, in pandas._libs.parsers.TextReader._check_tokenize_status
File "pandas/_libs/parsers.pyx", line 2053, in pandas._libs.parsers.raise_parser_error
File "<frozen codecs>", line 325, in decode
