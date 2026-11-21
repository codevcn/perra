.. _usage-examples:

Usage examples
==============

You can use Perra as:

- a command line tool: initial and a default mode
- a `web interface <#web-interface>`_: view the graph with results and download all report formats on a single page
- a library: integrate Perra into your own project

Use Cases
---------


1. Search for accounts with username ``machine42`` on top 500 sites (by default, according to Majestic Million rank) from the Perra DB.

.. code-block:: console

  perra machine42

2. Search for accounts with username ``machine42`` on **all sites** from the Perra DB.

.. code-block:: console

  perra machine42 -a

.. note::
   Perra will search for accounts on a huge number of sites,
   and some of them may return false positive results. At the moment, we are working on autorepair mode to deliver 
   the most accurate results. 
   
   If you experience many false positives, you can do the following:

   - Install the last development version of Perra from GitHub
   - Run Perra with ``--self-check --auto-disable`` flag and agree on disabling of problematic sites

3. Search for accounts with username ``machine42`` and generate HTML and PDF reports.

.. code-block:: console

  perra machine42 -HP

or

.. code-block:: console

  perra machine42 -a --html --pdf


4. Search for accounts with username ``machine42`` on Facebook only.

.. code-block:: console

  perra machine42 --site Facebook

5. Extract information from the Steam page by URL and start a search for accounts with found username ``machine42``.

.. code-block:: console

  perra --parse https://steamcommunity.com/profiles/76561199113454789 

6. Search for accounts with username ``machine42`` only on US and Japanese sites.

.. code-block:: console

  perra machine42 --tags us,jp

7. Search for accounts with username ``machine42`` only on sites related to software development.

.. code-block:: console

  perra machine42 --tags coding

8. Search for accounts with username ``machine42`` on uCoz sites only (mostly CIS countries).

.. code-block:: console

  perra machine42 --tags ucoz

