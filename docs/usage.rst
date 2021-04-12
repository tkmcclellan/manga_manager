=====
Usage
=====

manga_manager has five (5) commands: ``list``, ``add``, ``remove``, ``edit``, and ``read``.

Commands can be issued directly from the command line, or, by simply entering ``manga``, manga_manager
will open its starting menu where commands can be issued repeatedly. Users can exit the menu by
entering ``quit`` or Ctrl-c.

.. code-block:: console

    $ manga

When using commands from the menu, the script name ``manga`` does not need to be used.

List
----
``list`` lists the manga tracked by manga_manager. To list manga, enter:

.. code-block:: console

    $ manga list


Add
---
``add`` adds a manga to manga_manager's tracker. To add Attack on Titan to manga_manager, enter:

.. code-block:: console

    $ manga add attack on titan

This command also has optional flags:

* ``-p``, ``--provider``: The online manga provider (default: Mangakakalot).
* ``-dm``, ``--download_mode``: The method for downloading manga. Options include ``dynamic``, which will download and delete manga chapters as you read, ``all``, which will download all chapters of a manga at once, and ``none``, which will not download any chapters upon adding the manga (default: ``dynamic``).

To download all of Attack on Titan:

.. code-block:: console

    $ manga add attack on titan --download_mode all

Remove
------
``remove`` removes a manga from manga_manager. It will also delete any locally downloaded chapters.

.. code-block:: console

    $ manga remove attack on titan

Edit
----
``edit`` allows for editing the saved configuration of a manga. Using this command will list the modifyable configurations
and prompt the user to edit them.

.. code-block:: console

    $ manga edit attack on titan

Read 
----
``read`` allows the user to read manga. This command will open the most recently read chapter of a manga
in the user's web browser. After reading the chapter, users will be prompted to read the next chapter, go back
to the previous chapter, or quit reading.

To read Attack on Titan:

.. code-block:: console

    $ manga read attack on titan

``read`` also has the optional flag ``-c``, ``--chapters`` which allows the user to specify which chapter they want
to read.

To read chapter 10 of Attack on Titan:

.. code-block:: console

    $ manga read attack on titan -c 10

Footnote
~~~~~~~~
If using manga_manager's menu, all commands entered above will work without the keyword ``manga``. For example, ``manga read attack on titan`` would be ``read attack on titan`` when using the menu.
