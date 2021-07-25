# process-manager

The process manager python module for the DMIC-CADE arcade system. 🕹

Run with: `python3 -m dmicade_pm`

---

#### Command Line Options:

Option | Function
------ | --------
`--log=<log-level>` | Output [log level](https://docs.python.org/3/howto/logging.html).
`--debug` | Starts in debug mode. (Msg parser input via console for now...)

You can overwrite any default property from [default_pm_config.json](/dmicade_pm/default_pm_config.json) with comand line options.

Format:

`--<property>` or `--<property>=<value>`

Example for running with 2min game timeout and loglevel 'debug':

`python3 -m dmicade_pm --game_timeout=120 --log=DEBUG`
