import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.game_launcher as launcher
import pathlib


class OSRSMyBot(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "First Bot"
        description = "<Bot description here.>"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.take_breaks = True

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("take_breaks", "Take breaks?", ["Yes", "No"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":  # <-- Add this line
                self.take_breaks = options[option] == "Yes" # <-- Add this line
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.") # <-- Add this line
        self.log_msg("Options set successfully.")
        self.options_set = True

    def launch_game(self):
        pass

    def launch_game(self):
        # If playing RSPS, change `RuneLite` to the name of your game
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return
    
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="OSBCSandstone",  # Supply a name if you'd like to save it to PM permanently
            callback=self.log_msg,
    )

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. To see what the APIs can offer you, see here: https://github.com/kelltom/OSRS-Bot-COLOR/tree/main/src/utilities/api.
          For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.` operator to access their
          functions.
        """
        # Setup APIs
        api_m = MorgHTTPSocket()
        api_status = StatusSocket()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 600
        while time.time() - start_time < end_time:

            # 5% chance to take a break between clicks
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=2)
            
 
            time.sleep(3)
            if api_status.get_is_inv_full():
                self.log_msg("Inventory is full")
                if grinder := self.get_nearest_tag(clr.RED):
                    self.log_msg("got nearest blue tag")
                    self.log_msg(f"moving mouse to grinder")
                    self.mouse.move_to(grinder.random_point())
                    if not self.mouseover_text(contains="Deposit"):
                        self.log_msg(f"mouse over txt does not contain Deposit")
                        continue
                    self.log_msg(f"clicking on Deposit")
                    self.mouse.click()
                self.log_msg(f"Grinder not found")
                time.sleep(1)

            elif api_m.get_is_player_idle():
                if ore := self.get_nearest_tag(clr.PINK):
                        self.mouse.move_to(ore.random_point(), mouseSpeed="fastest")
                        if not self.mouseover_text(contains="Mine"):
                            continue
                        self.mouse.click()
                

            # if api_m.get_is_player_idle():
            #     self.log_msg("Idle, keep mining")
            #     if ore := self.get_nearest_tag(clr.BLACK):
            #         self.mouse.move_to(ore.random_point())
            #         if not self.mouseover_text(contains="Board"):
            #             continue
            #         self.mouse.click()



            self.update_progress((time.time() - start_time) / end_time)
        
        

        self.update_progress(1)
        self.log_msg("Finished.")
        self.set_status(BotStatus.STOPPED)