# To install:
pip install -r requirements.txt (or requirements\_test.txt if you want to run tests)
You also need to install OpenCV with ffmpeg support

# To run
Find a streamer that is playing overwatch and type:
`python run.py some\_streamer`

# Todo
* parallelization (`get_most_likely_heroes` is really slow)
* generalize (this shouldn't be overwatch specific)

# Run tests
`python -m tests.test`
