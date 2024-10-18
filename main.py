import os.path
import random
import time

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
import songs
from db_functions import (add_song_to_database_table,  # ... other imports
    fetch_all_songs_from_database_table, delete_song_from_database_table, delete_database_table,
    delete_all_songs_from_database_table, get_all_schemas, supabase,
    get_all_playlists, get_playlist_songs, delete_playlist, create_playlist, add_song_to_playlist)



from music import Ui_MusicApp
from PyQt5.QtCore import Qt, QUrl, QTimer

from playlist_popup import PlaylistDialog

class ModernMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        # Remove default title bar
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Globals
        global stopped
        global looped
        global is_shuffled
        global slide_index

        stopped = False
        looped = False
        is_shuffled = False
        slide_index = 0

        # Context Menus
        self.playlist_context_menu()
        self.loaded_songs_context_menu()
        self.favourite_songs_context_menu()

        # Database Stuff
        self.schema_name = "public"  # Or your schema name
        self.load_favourites_into_app()
        self.load_playlists()

        # Create Player
        self.player = QMediaPlayer() # Initialize the player object before connecting signals
        self.player.durationChanged.connect(self.set_slider_range) # Connect after defining the method

        self.initial_volume = 20
        self.player.setVolume(self.initial_volume)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f'{self.initial_volume}')
        self.player.durationChanged.connect(self.set_slider_range)


        # Initial position of the window
        self.initialPosition = self.pos()

        # Slider Timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)

        # Connections
        # DEFAULT PAGE
        self.player.mediaStatusChanged.connect(self.song_finished)
        self.player.mediaChanged.connect(self.slideshow)
        self.music_slider.sliderMoved[int].connect(
            lambda: self.player.setPosition(self.music_slider.value())
        )
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.loop_one_btn.clicked.connect(self.loop_one_song)
        self.delete_selected_btn.clicked.connect(self.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)
        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)

        self.volume_dial.valueChanged.connect(lambda: self.volume_changed())
        self.add_to_fav_btn.clicked.connect(self.add_song_to_favourites)

        # Default Page Actions
        self.actionPlay.triggered.connect(self.play_song)
        self.actionPause_Unpause.triggered.connect(self.pause_and_unpause)
        self.actionNext.triggered.connect(self.next_song)
        self.actionPrevious.triggered.connect(self.previous_song)
        self.actionStop.triggered.connect(self.stop_song)

        # FAVOURITES
        self.delete_selected_favourite_btn.clicked.connect(self.remove_song_from_favourites)
        self.delete_all_favourites_btn.clicked.connect(self.remove_all_songs_from_favourites)

        # Favourite Actions
        self.actionAdd_Selected_to_Favourites.triggered.connect(self.add_song_to_favourites)
        self.actionAdd_all_to_Favouries.triggered.connect(self.add_all_songs_to_favourites)
        self.actionRemove_Selected_Favourite.triggered.connect(self.remove_song_from_favourites)
        self.actionRemove_All_Favourites.triggered.connect(self.remove_all_songs_from_favourites)

        # PLAYLISTS
        self.playlists_listWidget.itemDoubleClicked.connect(self.show_playlist_content)
        self.new_playlist_btn.clicked.connect(self.new_playlist)
        self.remove_selected_playlist_btn.clicked.connect(self.delete_playlist)
        self.remove_all_playlists_btn.clicked.connect(self.delete_all_playlists)
        self.add_to_playlist_btn.clicked.connect(self.add_currently_playing_to_a_playlist)
        try:
            self.load_selected_playlist_btn.clicked.connect(
                lambda: self.load_playlist_songs_to_current_list(
                    self.playlists_listWidget.currentItem().text()
                )
            )

            self.actionLoad_Selected_Playlist.triggered.connect(
                lambda: self.load_playlist_songs_to_current_list(
                    self.playlists_listWidget.currentItem().text()
                )
            )
        except:
            pass

        # Playlist Actions
        self.actionSave_all_to_a_playlist.triggered.connect(self.add_all_current_songs_to_a_playlist)
        self.actionSave_Selected_to_a_Playlist.triggered.connect(self.add_a_song_to_a_playlist)
        self.actionDelete_All_Playlists.triggered.connect(self.delete_all_playlists)
        self.actionDelete_Selected_Playlist.triggered.connect(self.delete_playlist)

        self.show()

        def moveApp(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.initialPosition)
                self.initialPosition = event.globalPos()
                event.accept()

        self.title_frame.mouseMoveEvent = moveApp

    def set_slider_range(self, duration):  # Correct indentation: at the same level as __init__
        self.music_slider.setRange(0, duration)
    
    # Function to handle mouse position
    def mousePressEvent(self, event):
        self.initialPosition = event.globalPos()

    # Function to determine the end of the song
    def song_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()

    # Function to move the slider
    def move_slider(self):
        if stopped:
            return
        else:
        # Update the slider
            if self.player.state() == QMediaPlayer.PlayingState:
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                slider_position = self.player.position()
                self.music_slider.setValue(slider_position)

            # Change time labels
            current_time = time.strftime("%H:%M:%S", time.localtime(self.player.position() / 1000))
            song_duration = time.strftime("%H:%M:%S", time.localtime(self.player.duration() / 1000))
            self.time_label.setText(f"{current_time} / {song_duration}")


    # Add Songs
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Songs to the app', directory=':\\',
            filter='Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)'
        )
        if files:
            for file in files:
                songs.current_song_list.append(file)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(file)

                    )
                )

    # Play Song
    def play_song(self):
        try:
            global stopped
            stopped = False

            if self.stackedWidget.currentIndex() == 0:
                current_selection = self.loaded_songs_listWidget.currentRow()
                current_song = songs.current_song_list[current_selection]  # From current list
            elif self.stackedWidget.currentIndex() == 2:
                current_selection = self.favourites_listWidget.currentRow()
                current_song = songs.favourites_songs_list[current_selection]  # From favorites list
            
            self.music_slider.setValue(0)  # Reset slider position to 0
            self.time_label.setText("00:00:00 / 00:00:00") # Reset the time label text

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.setPosition(0)  # Set position *after* setMedia

            self.music_slider.setValue(0)
            self.music_slider.update()  # or self.music_slider.repaint()
            self.time_label.setText("00:00:00 / 00:00:00")
            self.player.play()

            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"play song error: {e}")

    # Pause and Unpause
    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    # Stop Song
    def stop_song(self):
        try:
            self.player.stop()
            self.music_slider.setValue(0)
            self.music_slider.update()
            self.time_label.setText(f'00:00:00 / 00:00:00')
            self.current_song_name.setText(f'Song name goes here')
            self.current_song_path.setText(f'Song path goes here')
        except Exception as e:
            print(f"Stop song error: {e}")

    # Function to change the volume
    def volume_changed(self):
        try:
            self.initial_volume = self.volume_dial.value()
            self.player.setVolume(self.initial_volume)
        except Exception as e:
            print(f"Volume change error: {e}")

    def default_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.current_song_list.index(current_song_url)
                if song_index + 1 == len(songs.current_song_list):
                    next_index = 0
                else:
                    next_index = song_index + 1
                next_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.favourites_songs_list.index(current_song_url)
                if song_index + 1 == len(songs.favourites_songs_list):
                    next_index = 0
                else:
                    next_index = song_index + 1
                next_song = songs.favourites_songs_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)

            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')
        except Exception as e:
            print(f"Default Next error: {e}")

    def looped_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.current_song_list.index(current_song_url)

                song = songs.current_song_list[song_index]
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.favourites_songs_list.index(current_song_url)

                song = songs.favourites_songs_list[song_index]
            song_url = QMediaContent(QUrl.fromLocalFile(song))
            self.player.setMedia(song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(song_index)

            self.current_song_name.setText(f'{os.path.basename(song)}')
            self.current_song_path.setText(f'{os.path.dirname(song)}')
        except Exception as e:
            print(f"Looped Next: {e}")

    def shuffled_next(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                next_index = random.randint(0, len(songs.current_song_list))
                next_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget.currentIndex() == 2:
                next_index = random.randint(0, len(songs.favourites_songs_list))
                next_song = songs.favourites_songs_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)
            song_url = QMediaContent(QUrl.fromLocalFile(next_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')
        except Exception as e:
            print(f"Shuffled next error: {e}")

    # Play Next Song
    def next_song(self):
        try:
            global looped
            global is_shuffled

            if is_shuffled:
                self.shuffled_next()
            elif looped:
                self.looped_next()
            else:
                self.default_next()

        except Exception as e:
            print(f"Next Song error: {e}")

    # Play Next Song
    def previous_song(self):
        try:
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.current_song_list.index(current_song_url)
                if song_index == 0:
                    previous_index = len(songs.current_song_list) - 1
                else:
                    previous_index = song_index - 1
                previous_song = songs.current_song_list[previous_index]
                self.loaded_songs_listWidget.setCurrentRow(previous_index)
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]

                song_index = songs.favourites_songs_list.index(current_song_url)
                if song_index == 0:
                    previous_index = len(songs.favourites_songs_list) - 1
                else:
                    previous_index = song_index - 1
                previous_song = songs.favourites_songs_list[previous_index]
                self.favourites_listWidget.setCurrentRow(previous_index)
            song_url = QMediaContent(QUrl.fromLocalFile(previous_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.current_song_name.setText(f'{os.path.basename(previous_song)}')
            self.current_song_path.setText(f'{os.path.dirname(previous_song)}')

        except Exception as e:
            print(f"Next Song error: {e}")

    # Function to loop the song
    def loop_one_song(self):
        try:
            global is_shuffled
            global looped

            if not looped:
                looped = True
                self.shuffle_songs_btn.setEnabled(False)
            else:
                looped = False
                self.shuffle_songs_btn.setEnabled(True)
        except Exception as e:
            print(f"Looping song error: {e}")

    # Function to shuffle the songs
    def shuffle_playlist(self):
        try:
            global is_shuffled
            global looped

            if not is_shuffled:
                is_shuffled = True
                self.loop_one_btn.setEnabled(False)
            else:
                is_shuffled = False
                self.loop_one_btn.setEnabled(True)
        except Exception as e:
            print(f"Shuffling song error: {e}")

    # Remove One Song
    def remove_selected_song(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove Selected Song',
                    'Playlist is empty'
                )
                return
            current_index = self.loaded_songs_listWidget.currentRow()
            self.loaded_songs_listWidget.takeItem(current_index)
            songs.current_song_list.pop(current_index)
        except Exception as e:
            print(f"Remove selected song error: {e}")

    # Remove One Song
    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove all Songs',
                    'Playlist is empty'
                )
                return
            question = QMessageBox.question(
                self, 'Remove all Songs',
                'This action will remove all songs from the list and it cannot be reversed.\n'
                'Continue?',
                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if question == QMessageBox.Yes:
                self.stop_song()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()

        except Exception as e:
            print(f"Remove all songs error: {e}")

    # FUNCTIONS TO SWITCH TABS
    # Switch to Favourites tab
    def switch_to_favourites_tab(self):
        self.stackedWidget.setCurrentIndex(2)

    # Switch to Playlists Tab
    def switch_to_playlist_tab(self):
        self.stackedWidget.setCurrentIndex(1)

    # Switch to Song List tab
    def switch_to_songs_tab(self):
        self.stackedWidget.setCurrentIndex(0)

    # FAVOURITE FUNCTIONS
    # Load Favourite songs
    def load_favourites_into_app(self):
        favourite_songs = fetch_all_songs_from_database_table('favourites')  # Now using Supabase function
        songs.favourites_songs_list.clear()
        self.favourites_listWidget.clear()

        if favourite_songs is None:
            favourite_songs = []
        for favourite in favourite_songs:
            songs.favourites_songs_list.append(favourite)
            self.favourites_listWidget.addItem(
                QListWidgetItem(
                    QIcon(":/img/utils/images/like.png"),
                    os.path.basename(favourite)
                )
            )

    # Add all songs to favourites
    def add_all_songs_to_favourites(self):
        if not songs.current_song_list:  # Check if current list is empty
            QMessageBox.information(
                self, 'Add songs to favourites',
                'No songs have been loaded'
            )
            return
        for song in songs.current_song_list:
            add_song_to_database_table(song, 'favourites')
        self.load_favourites_into_app()

    # Add song to favourites
    def add_song_to_favourites(self):
        current_index = self.loaded_songs_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Add Songs to Favourites',
                'Select a song to add to favourites'
            )
            return
        try:
            song = songs.current_song_list[current_index]
            add_song_to_database_table(song=f"{song}", table='favourites')
            # QMessageBox.information(
            #     self, 'Add Songs to Favourites',
            #     f'{os.path.basename(song)} was successfully added to favourites'
            # )
            self.load_favourites_into_app()
        except Exception as e:
            print(f"Adding song to favourites error: {e}")

    # Remove song from favourites
    def remove_song_from_favourites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove Song from Favourites',
                'Favourites list is empty'
            )
            return
        current_index = self.favourites_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Remove Song from Favourites',
                'Select a song to remove from favourites'
            )
            return
        try:
            song = songs.favourites_songs_list[current_index]
            delete_song_from_database_table(song=f'{song}', table='favourites')
            self.load_favourites_into_app()
        except Exception as e:
            print(f"Removing from favourites error: {e}")

    # Remove all songs from favourites
    def remove_all_songs_from_favourites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove Song from Favourites',
                'Favourites list is empty'
            )
            return
        question = QMessageBox.question(
            self, 'Remove all favourite songs',
            'This action will remove all songs from Favourites and it cannot be reversed.\n'
            'Continue?',
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
        )
        if question == QMessageBox.Yes:
            try:

                delete_all_songs_from_database_table(table='favourites')
                self.load_favourites_into_app()
            except Exception as e:
                print(f"Removing all songs from favourites error: {e}")

    # PLAYLIST FUNCTIONS
    # Load Playlists into app
    def load_playlists(self):
        playlists = get_all_playlists() # Using Supabase function to fetch tables
        self.playlists_listWidget.clear()
        for playlist in playlists:
            self.playlists_listWidget.addItem(
                QListWidgetItem(
                    QIcon(":/img/utils/images/dialog-music.png"),
                    playlist
                )
            )

    # Create a new playlist
        # ... in main.py
    def new_playlist(self):
        try:
            existing_playlists = get_all_playlists()
            name, ok = QtWidgets.QInputDialog.getText(self, 'Create a new playlist', 'Enter playlist name')
            if not ok:
                return  # No input received

            if not name.strip():
                QMessageBox.information(self, 'Name Error', 'Playlist name cannot be empty')
                return

            if name in existing_playlists:  # If playlist already exists
                caution = QMessageBox.question(
                    self, 'Replace Playlist',
                    f'A playlist with name "{name}" already exists.\n'  # Clearer message
                    'Do you want to replace it?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel  # Add "No" option
                )

                if caution == QMessageBox.Yes:
                    delete_playlist(name)  # Delete existing playlist and its songs
                elif caution == QMessageBox.No: # Do nothing if No is pressed
                    pass # Or you could add a message saying the playlist was not created
                else:  # User cancelled (QMessageBox.Cancel)
                    return  # Exit the function

            create_playlist(name)  # Create the new playlist (only if it's new or replaced)
            self.load_playlists()  # Refresh playlist display

        except Exception as e:
            print(f"Creating a new playlist error: {e}")
            QMessageBox.critical(self, "Error", f"Could not create playlist: {e}")

    # Delete a playlist
    def delete_playlist(self):
        try:
            playlist_name = self.playlists_listWidget.currentItem().text()
            delete_playlist(playlist_name) # Delete playlist from playlists table
        except Exception as e:
            print(f"Deleting playlist error: {e}")
        finally:
            self.load_playlists()

    # Delete all playlists
    def delete_all_playlists(self):
        playlists = get_all_playlists()
        playlists.remove('favourites')

        caution = QMessageBox.question(
            self, 'Delete all playlists',
            'This action will delete all playlists and it cannot be reversed.\n'
            'Continue?',
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
        )
        if caution == QMessageBox.Yes:
            try:
                for playlist in playlists:
                    delete_database_table(playlist)
            except Exception as e:
                print(f"Deleting all playlists error: {e}")
            finally:
                self.load_playlists()

    def add_a_song_to_a_playlist(self):
        options = get_all_playlists()  # Get playlist *names*
        if not options:  # Handle case where there are no playlists
            QMessageBox.information(self, "No Playlists", "Create a playlist first.")
            return

        options.insert(0, '--Click to Select--')
        playlist_name, _ = QtWidgets.QInputDialog.getItem(  # Get selected playlist name
            self, 'Add song to playlist', 'Choose the desired playlist', options, editable=False
        )
        if playlist_name == '--Click to Select--':
            return  # No playlist selected

        try:
            current_index = self.loaded_songs_listWidget.currentRow()
            song = songs.current_song_list[current_index]
            add_song_to_playlist(playlist_name, song)  # Use the correct function
        except Exception as e:
            QMessageBox.information(self, 'Unsuccessful', 'No song was selected')
            return
        add_song_to_playlist(playlist_name, song)

    # Add all current songs to a playlist
    def add_all_current_songs_to_a_playlist(self):
        options = get_all_playlists()
        options.remove('favourites')
        options.insert(0, '--Click to Select--')
        playlist, _ = QtWidgets.QInputDialog.getItem(
            self, 'Add song to playlist',
            'Choose the desired playlist', options, editable=False
        )
        if playlist == '--Click to Select--':
            QMessageBox.information(self, 'Add song to playlist', 'No playlist was selected')
            return
        if len(songs.current_song_list) < 1:
            QMessageBox.information(
                self, 'Add songs to playlist',
                'Song list is empty'
            )
            return
        for song in songs.current_song_list:
            add_song_to_database_table(song=song, table=playlist)
        self.load_playlists()

    # Add currently playing to a playlist
    def add_currently_playing_to_a_playlist(self):
        if not self.player.state() == QMediaPlayer.PlayingState:
            QMessageBox.information(
                self, 'Add current song to playlist',
                'No song is playing in queue.'
            )
            return
        options = get_all_playlists()
        options.remove('favourites')
        options.insert(0, '--Click to Select--')
        playlist_name, _ = QtWidgets.QInputDialog.getItem(
            self, 'Add song to playlist',
            'Choose the desired playlist', options, editable=False
        )
        if playlist_name == '--Click to Select--':
            QMessageBox.information(self, 'Add song to playlist', 'No playlist was selected')
            return

        current_media = self.player.media()
        song = current_media.canonicalUrl().path()[1:]
        add_song_to_playlist(playlist_name, song)
        self.load_playlists()

    # Load playlists songs to current list
    def load_playlist_songs_to_current_list(self, playlist):
        try:
            playlist_songs = fetch_all_songs_from_database_table(playlist)
            if len(playlist_songs) == 0:
                QMessageBox.information(
                    self, 'Load playlist song',
                    'Playlist is empty'
                )
                return
            for song in playlist_songs:
                songs.current_song_list.append(song)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(song)
                    )
                )
        except Exception as e:
            print(f"Loading songs from playlist: {playlist}: {e}")

    # Show Playlist Content
    def show_playlist_content(self):
        try:
            playlist_name = self.playlists_listWidget.currentItem().text() # Get playlist name
            songs_in_playlist = get_playlist_songs(playlist_name)  # Get songs from db_functions
            song_names = [os.path.basename(song) for song in songs_in_playlist]
            playlist_dialog = PlaylistDialog(song_names, playlist_name)
            playlist_dialog.exec_()
        except Exception as e:
            print(f"Showing Playlist Content error: {e}")

    # CONTEXT MENUS
    # Playlist Contex Menu
    def playlist_context_menu(self):
        self.playlists_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.playlists_listWidget.addAction(self.actionLoad_Selected_Playlist)
        separator = QAction(self)
        separator.setSeparator(True)
        self.playlists_listWidget.addAction(self.actionDelete_Selected_Playlist)
        self.playlists_listWidget.addAction(self.actionDelete_All_Playlists)

    # Loaded Songs Context Menu
    def loaded_songs_context_menu(self):
        self.loaded_songs_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.loaded_songs_listWidget.addAction(self.actionPlay)
        self.loaded_songs_listWidget.addAction(self.actionPause_Unpause)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionPrevious)
        self.loaded_songs_listWidget.addAction(self.actionNext)
        self.loaded_songs_listWidget.addAction(self.actionStop)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionAdd_Selected_to_Favourites)
        self.loaded_songs_listWidget.addAction(self.actionAdd_Selected_to_Favourites)
        self.loaded_songs_listWidget.addAction(self.actionAdd_all_to_Favouries)
        separator = QAction(self)
        separator.setSeparator(True)
        self.loaded_songs_listWidget.addAction(self.actionSave_Selected_to_a_Playlist)
        self.loaded_songs_listWidget.addAction(self.actionSave_all_to_a_playlist)

    # Favourite Songs Context Menu
    def favourite_songs_context_menu(self):
        self.favourites_listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.favourites_listWidget.addAction(self.actionRemove_Selected_Favourite)
        self.favourites_listWidget.addAction(self.actionRemove_All_Favourites)

    # Slideshow
    def slideshow(self):
        images_path = os.path.join(os.getcwd(), os.path.join('utils', 'bg_imgs'))
        images = os.listdir(images_path)
        images.remove('bg_overlay.png')
        global slide_index

        next_slide = images[slide_index]
        next_image = QtGui.QPixmap(os.path.join(images_path, f'{next_slide}'))
        self.background_image.setPixmap(next_image)
        slide_index += 1
