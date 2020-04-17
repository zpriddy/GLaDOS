from typing import List, Union

import yaml

from glados import PyJSON, logging


class GladosConfig:
    def __init__(self, config_file: str):
        self.config = None  #  type: Union[None, PyJSON]
        self.config_file = config_file

    def read_config(self):
        """Read the config file into a config object"""
        logging.debug(f"loading glados config")
        try:
            with open(self.config_file) as file:
                c = yaml.load(file, yaml.FullLoader)
                self.config = PyJSON(c)
        except FileNotFoundError as e:
            logging.critical(f"glados config file not found: {self.config_file} - {e}")
            raise FileNotFoundError(e)
        except OSError as e:
            logging.critical(
                f"error reading glados config file: {self.config_file} - {e}"
            )
            raise OSError(e)
        except yaml.YAMLError as e:
            logging.critical(
                f"error reading yaml in glados config file: {self.config_file} - {e}"
            )
            raise yaml.YAMLError(e)

    @property
    def sections(self) -> List[str]:
        """what sections are there in the config file
        
        Returns
        -------
            sorted list of sections in the yaml file
        """
        if not self.config:
            return list()
        return sorted(list(self.config.to_dict().keys()))
