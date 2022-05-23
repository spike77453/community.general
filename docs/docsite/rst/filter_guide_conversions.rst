Conversions
-----------

Parsing CSV files
^^^^^^^^^^^^^^^^^

Ansible offers the :ref:`community.general.read_csv module <ansible_collections.community.general.read_csv_module>` to read CSV files. Sometimes you need to convert strings to CSV files instead. For this, the ``from_csv`` filter exists.

.. code-block:: yaml+jinja

    - name: "Parse CSV from string"
      debug:
        msg: "{{ csv_string | community.general.from_csv }}"
      vars:
        csv_string: |
          foo,bar,baz
          1,2,3
          you,this,then

This produces:

.. code-block:: ansible-output

    TASK [Parse CSV from string] **************************************************************
    ok: [localhost] => {
        "msg": [
            {
                "bar": "2",
                "baz": "3",
                "foo": "1"
            },
            {
                "bar": "this",
                "baz": "then",
                "foo": "you"
            }
        ]
    }

The ``from_csv`` filter has several keyword arguments to control its behavior:

:dialect: Dialect of the CSV file. Default is ``excel``. Other possible choices are ``excel-tab`` and ``unix``. If one of ``delimiter``, ``skipinitialspace`` or ``strict`` is specified, ``dialect`` is ignored.
:fieldnames: A set of column names to use. If not provided, the first line of the CSV is assumed to contain the column names.
:delimiter: Sets the delimiter to use. Default depends on the dialect used.
:skipinitialspace: Set to ``true`` to ignore space directly after the delimiter. Default depends on the dialect used (usually ``false``).
:strict: Set to ``true`` to error out on invalid CSV input.

.. versionadded: 3.0.0

Converting to JSON
^^^^^^^^^^^^^^^^^^

`JC <https://pypi.org/project/jc/>`_ is a CLI tool and Python library which allows to interpret output of various CLI programs as JSON. It is also available as a filter in community.general. This filter needs the `jc Python library <https://pypi.org/project/jc/>`_ installed on the controller.

.. code-block:: yaml+jinja

    - name: Run 'ls' to list files in /
      command: ls /
      register: result

    - name: Parse the ls output
      debug:
        msg: "{{ result.stdout | community.general.jc('ls') }}"

This produces:

.. code-block:: ansible-output

    TASK [Run 'ls' to list files in /] ********************************************************
    changed: [localhost]

    TASK [Parse the ls output] ****************************************************************
    ok: [localhost] => {
        "msg": [
            {
                "filename": "bin"
            },
            {
                "filename": "boot"
            },
            {
                "filename": "dev"
            },
            {
                "filename": "etc"
            },
            {
                "filename": "home"
            },
            {
                "filename": "lib"
            },
            {
                "filename": "proc"
            },
            {
                "filename": "root"
            },
            {
                "filename": "run"
            },
            {
                "filename": "tmp"
            }
        ]
    }

.. versionadded: 2.0.0

TOML
^^^^

`TOML <https://github.com/toml-lang/toml>`_ is a file format for configuration files. With the help of the `toml Python library <https://pypi.org/project/toml/>`_ conversion of a dictionary to TOML or conversion of a TOML-formatted string to a dictionary is available as a filter in community.general.

These filters need the `toml Python library <https://pypi.org/project/toml/>`_ installed on the controller.

Converting to TOML
""""""""""""""""""

You can create a TOML-formatted string from any variable with the ``to_toml`` filter:

.. code-block:: yaml+jinja

    - name: Convert variable into toml file and write to file
      ansible.builtin.copy:
        content: "{{ gitlab_runner_config | community.general.to_toml }}"
        dest: /etc/gitlab-runner/config.toml
      vars:
        - gitlab_runner_config:
            concurrent: 2
            check_interval: 2
            session_server:
            session_timeout: 1800
            runners:
            - name: "gitlab-runner.example.com"
                url: "https://gitlab.example.com"
                token: supersecrettoken
                executor: docker
                docker:
                tls_verify: true
                image: "fedora:latest"
                privileged: false
                disable_entrypoint_overwrite: false
                oom_kill_disable: false
                disable_cache: false
                volumes: ["/cache"]
                shm_size: 0

This creates a file with the following content:

.. code-block:: toml

    concurrent = 2
    check_interval = 2
    [[runners]]
    name = "gitlab-runner.example.com"
    url = "https://gitlab.example.com"
    token = "supersecrettoken"
    executor = "docker"

    [runners.docker]
    tls_verify = true
    image = "fedora:latest"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = [ "/cache",]
    shm_size = 0

    [session_server]
    session_timeout = 1800

This also works on ``hostvars``:

.. code-block:: yaml+jinja

    - name: Convert hostvars into toml file
      ansible.builtin.copy:
        content: "{{ hostvars['gitlab_runner']['runner_config'] | community.general.to_toml }}"
        dest: /etc/gitlab-runner/config.toml

.. versionadded: 5.1.0

Converting from TOML
""""""""""""""""""""

Simliar to the ``to_toml`` filter you can create a dictionary from any TOML-formatted string by using the ``from_toml`` filter:

.. code-block:: yaml+jinja

    - name: Convert TOML-formatted data into dictionary
      debug:
        msg: "{{ toml | community.general.from_toml | community.general.json_query('runners[0].token') }}"
      vars:
        - toml: |
            concurrent = 2
            check_interval = 2
            [[runners]]
            name = "gitlab-runner.example.com"
            url = "https://gitlab.example.com"
            token = "supersecrettoken"
            executor = "docker"

            [runners.docker]
            tls_verify = true
            image = "fedora:latest"
            privileged = false
            disable_entrypoint_overwrite = false
            oom_kill_disable = false
            disable_cache = false
            volumes = [ "/cache",]
            shm_size = 0

            [session_server]
            session_timeout = 1800

This produces:

.. code-block:: ansible-output

    TASK [Convert TOML-formatted data into dictionary] ****************************************
    ok: [localhost] => {
        "msg": "supersecrettoken"
    }

This is probably most useful in combination with the :ref:`ansible.builtin.slurp module <ansible.builtin.slurp_module>`, e.g.:

.. code-block:: yaml+jinja

    - name: Get gitlab runner configuration
      slurp:
        src: /etc/gitlab-runner/config.toml
      register: slurped_config

    - name: Convert TOML-formatted data into dictionary
      debug:
        msg: "{{ slurped_config['content'] | b64decode | community.general.from_toml | json_query('runners[0].token') }}"

This produces:

.. code-block:: ansible-output

    TASK [Get gitlab runner configuration] ****************************************************
    ok: [localhost]

    TASK [Convert TOML-formatted data into dictionary] ****************************************
    ok: [localhost] => {
        "msg": "supersecrettoken"
    }

.. versionadded: 5.1.0
