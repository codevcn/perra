.. _installation:

Installation
============

Perra can be installed using pip, Docker, or simply can be launched from the cloned repo.
Also, it is available online via the `community Telegram bot <https://maigret.app/docs-en>`_,
source code of a bot is `available on GitHub <https://github.com/codevcn/perra-tg-bot>`_.

Windows Standalone EXE-binaries
-------------------------------

A standalone ``perra_standalone.exe`` for Windows is published in the
`Releases section <https://github.com/codevcn/perra/releases>`_ of the GitHub
repository. A fresh build is produced automatically after each commit to the
**main** and **dev** branches.

There are two ways to launch the EXE:

* **Double-click it from Explorer.** Perra will prompt you for a username,
  run a default search, and pause at the end so the printed report links
  remain on screen until you press Enter.
* **Run it from a terminal** for full control over options:

  1. Press ``Win+R``, type ``cmd``, and hit Enter (or use PowerShell).
  2. Change to the folder where you saved the file, e.g.
     ``cd %USERPROFILE%\Downloads``.
  3. Run it with at least one username:

     .. code-block:: bat

        perra.exe USERNAME
        perra.exe USERNAME --html       :: also save an HTML report
        perra.exe USERNAME --pdf        :: also save a PDF report
        perra.exe --help                :: list all options

Reports are written next to the EXE in a ``reports\`` subfolder.

Video guide on how to run it: https://youtu.be/qIgwTZOmMmM.

Code signing
------------

Windows binaries are built on GitHub Actions from this repository. The project
has applied to the `SignPath Foundation <https://signpath.org/>`_ for a free
code signing certificate; once issued, released Windows binaries will be signed
as part of the same automated build.


Cloud Shells and Jupyter notebooks
----------------------------------

In case you don't want to install Perra locally, you can use cloud shells and Jupyter notebooks.
Press one of the buttons below and follow the instructions to launch it in your browser.

.. only:: html

   .. image:: https://user-images.githubusercontent.com/27065646/92304704-8d146d80-ef80-11ea-8c29-0deaabb1c702.png
      :target: https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/codevcn/perra&tutorial=README.md
      :alt: Open in Cloud Shell

   .. image:: https://replit.com/badge/github/codevcn/perra
      :target: https://repl.it/github/codevcn/perra
      :alt: Run on Replit
      :height: 50

   .. image:: https://colab.research.google.com/assets/colab-badge.svg
      :target: https://colab.research.google.com/gist/soxoj/879b51bc3b2f8b695abb054090645000/maigret-collab.ipynb
      :alt: Open In Colab
      :height: 45

   .. image:: https://mybinder.org/badge_logo.svg
      :target: https://mybinder.org/v2/gist/soxoj/9d65c2f4d3bec5dd25949197ea73cf3a/HEAD
      :alt: Open In Binder
      :height: 45

.. only:: latex

   Cloud Shell: https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/codevcn/perra&tutorial=README.md

   Replit: https://repl.it/github/codevcn/perra

   Google Colab: https://colab.research.google.com/gist/soxoj/879b51bc3b2f8b695abb054090645000/maigret-collab.ipynb

   Binder: https://mybinder.org/v2/gist/soxoj/9d65c2f4d3bec5dd25949197ea73cf3a/HEAD

Snap (Linux)
------------

Perra is on the `Snap Store <https://snapcraft.io/maigret>`_ for amd64 and
arm64. It needs neither Python nor pip:

.. only:: html

   .. image:: https://snapcraft.io/static/images/badges/en/snap-store-black.svg
      :target: https://snapcraft.io/maigret
      :alt: Get it from the Snap Store
      :height: 50

.. code-block:: bash

   sudo snap install perra

   # usage
   perra username

The snap is strictly confined: it can read and write your home directory and
very little else. Run it from a directory under ``$HOME`` and reports land in
``./reports`` as usual. Running it from somewhere it cannot see, ``/tmp`` for
instance, fails before the search starts.

Access to USB drives and other removable media is not connected by default:

.. code-block:: bash

   sudo snap connect perra:removable-media

Updates arrive on their own through snapd, so the bundled site database and the
code both stay current without any action.

Local installation from PyPi
----------------------------

Perra ships with a bundled site database. After installation from PyPI (or any other method), it can **automatically fetch a newer compatible database from GitHub** when you run it—see :ref:`database-auto-update` in :doc:`settings`.

.. note::
   Python 3.10 or higher and pip is required, **Python 3.11 is recommended.**

.. code-block:: bash

   # install from pypi
   pip3 install perra

   # usage
   perra username

PDF report support is shipped as an **optional extra** because it relies on
system-level graphics libraries that pip cannot install for you. If you plan to
use ``--pdf``, install Perra with the ``pdf`` extra:

.. code-block:: bash

   pip3 install 'perra[pdf]'

See :ref:`pdf-extra` below for the full background on why PDF support is
optional and how to fix the most common build errors.

Isolated installation with pipx
-------------------------------

``pip3 install perra`` drops Perra and its dependencies into whichever
Python environment happens to be active. If that is the system Python, the
install can collide with packages your distribution manages, and on recent
Debian, Ubuntu and Fedora pip refuses outright with
``error: externally-managed-environment``.

`pipx <https://pipx.pypa.io>`_ avoids all of that. It gives Perra its own
virtual environment, puts only the ``perra`` command on your ``PATH``, and
keeps the dependencies away from everything else on the machine:

.. code-block:: bash

   pipx install perra

   # usage
   perra username

The ``pdf`` extra works the same way:

.. code-block:: bash

   pipx install 'perra[pdf]'

Upgrading and removing are one command each:

.. code-block:: bash

   pipx upgrade perra
   pipx uninstall perra

.. note::
   If you already use `uv <https://docs.astral.sh/uv/>`_, ``uv tool install
   perra`` does the same job.

Development version (GitHub)
----------------------------

.. code-block:: bash

   git clone https://github.com/codevcn/perra && cd perra
   pip3 install .

   # OR
   pip3 install git+https://github.com/codevcn/perra.git

   # usage
   perra username

   # OR use poetry in case you plan to develop Perra
   pip3 install poetry
   poetry run perra

Docker
------

.. code-block:: bash

   # official image of the development version, updated from the github repo
   docker pull codevcn/perra

   # usage
   docker run -v /mydir:/app/reports codevcn/perra:latest username --html

   # manual build
   docker build -t perra .

Troubleshooting
---------------

If you encounter build errors during installation such as ``cannot find ft2build.h``
or errors related to ``reportlab`` / ``_renderPM``, you need to install system-level
dependencies required to compile native extensions.

**Debian/Ubuntu/Kali:**

.. code-block:: bash

   sudo apt install -y libfreetype6-dev libjpeg-dev libffi-dev

**Fedora/RHEL/CentOS:**

.. code-block:: bash

   sudo dnf install -y freetype-devel libjpeg-devel libffi-devel

**Arch Linux:**

.. code-block:: bash

   sudo pacman -S freetype2 libjpeg-turbo libffi

**macOS (Homebrew):**

.. code-block:: bash

   brew install freetype

After installing the system dependencies, retry the perra installation.

If you continue to have issues, consider using Docker instead, which includes all
necessary dependencies.

.. _pdf-extra:

Optional: PDF reports (``perra[pdf]``)
----------------------------------------

The ``--pdf`` report format is shipped as an optional extra. To enable it:

.. code-block:: bash

   pip3 install 'perra[pdf]'

If PDF support is not installed and you pass ``--pdf``, Perra prints a
warning and continues without crashing — every other output format
(``--html``, ``--json``, ``--csv``, ``--txt``, ``--xmind``, ``--graph``)
keeps working.

Why is PDF optional?
~~~~~~~~~~~~~~~~~~~~

Perra renders PDFs by converting an HTML template, and that conversion
pipeline ultimately depends on the ``cairo`` graphics library through a
chain of Python packages roughly shaped like::

   perra[pdf] → xhtml2pdf → svglib → rlPyCairo → pycairo → libcairo2 (system)

The bottom of that chain is a C library — ``libcairo2`` — that has to exist
on the host *before* pip can build the Python bindings. The Python binding
package (``pycairo``) currently ships **only Windows wheels** on PyPI; on
Linux and macOS pip falls back to building from source, and the build fails
the moment ``pkg-config`` cannot find ``cairo``. The error looks like::

   ../cairo/meson.build:31:12: ERROR: Dependency "cairo" not found (tried pkg-config)
   note: This error originates from a subprocess, and is likely not a problem with pip.
   error: metadata-generation-failed

Pulling this whole chain for every Perra install just so the much smaller
group of users who actually want PDFs can have them is a poor trade — so
``xhtml2pdf`` is gated behind the ``pdf`` extra.

Two more packages — ``arabic-reshaper`` and ``python-bidi`` — are bundled
into the same extra. Perra core never imports them; they are only used
by ``xhtml2pdf`` to shape Arabic glyphs and lay out right-to-left text in
PDFs. ``python-bidi`` v0.5+ is also a Rust binding, so on niche platforms
without a published wheel it would otherwise pull in a Cargo build for
users who never asked for PDF support.

Installing the system prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the cairo headers, ``pkg-config``, and a working C toolchain
*before* running ``pip install 'perra[pdf]'``.

**Debian / Ubuntu / Linux Mint / Kali:**

.. code-block:: bash

   sudo apt update
   sudo apt install -y libcairo2-dev pkg-config python3-dev build-essential
   pip3 install --upgrade pip setuptools wheel
   pip3 install 'perra[pdf]'

**Fedora / RHEL / CentOS:**

.. code-block:: bash

   sudo dnf install -y cairo-devel pkgconfig python3-devel gcc
   pip3 install 'perra[pdf]'

**Arch Linux:**

.. code-block:: bash

   sudo pacman -S cairo pkgconf base-devel
   pip3 install 'perra[pdf]'

**Alpine Linux:**

.. code-block:: bash

   sudo apk add cairo-dev pkgconf python3-dev build-base
   pip3 install 'perra[pdf]'

**macOS (Homebrew):**

.. code-block:: bash

   brew install cairo pkg-config
   pip3 install --upgrade pip setuptools wheel
   pip3 install 'perra[pdf]'

**Windows:**

No system packages are needed — ``pycairo`` ships prebuilt wheels for
Windows. Just run:

.. code-block:: bash

   pip install 'perra[pdf]'

**Google Cloud Shell / Colab / Replit / generic CI:**

These environments behave like Debian/Ubuntu — install the same
``libcairo2-dev pkg-config python3-dev build-essential`` triple before
``pip install 'perra[pdf]'``. If you do not control the base image and
cannot ``apt install``, skip the extra and use ``--html`` reports instead;
HTML reports contain the same data and open in any browser.

``perra: command not found`` after install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If pip prints warnings like::

   WARNING: The script perra is installed in
   '/home/<user>/.local/bin' which is not on PATH.

…and ``perra --version`` then fails with ``command not found``, your
``--user`` install put the entry-point script in a directory the shell does
not search. Add it to ``PATH``:

.. code-block:: bash

   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc

Or install into a virtual environment, where the entry point lands in the
venv's ``bin/`` automatically:

.. code-block:: bash

   python3 -m venv ~/.venvs/perra
   source ~/.venvs/perra/bin/activate
   pip install 'perra[pdf]'   # or just `pip install perra`

Optional: Cloudflare bypass solver
----------------------------------

.. warning::

   **Experimental.** The Cloudflare webgate is under active development;
   the configuration schema and CLI behaviour may change without
   backwards-compatibility guarantees.

Sites tagged ``cf_js_challenge`` / ``cf_firewall`` need a real browser to pass
their JavaScript challenge. To check those sites you can run a local
`FlareSolverr <https://github.com/FlareSolverr/FlareSolverr>`_ instance —
Perra will route protected checks to it when ``--cloudflare-bypass`` is set:

.. code-block:: bash

   docker run -d -p 8191:8191 --name flaresolverr ghcr.io/flaresolverr/flaresolverr:latest

This is **optional** — Perra runs without it; only sites whose
``protection`` field intersects ``settings.cloudflare_bypass.trigger_protection``
require the solver. See :ref:`cloudflare-bypass` for details.
