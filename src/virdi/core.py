
class Session:
    """Represents a single experimental session with associated data files"""
    
    def __init__(self, session_data: dict):
        
        self.data_paths = session_data


    def _repr_html_(self):

        html_text = ""
        for data_name, data_path in self.data_paths.items():
            html_text += f"<div style='padding-left:10px'><strong>{data_name}</strong>: ...{str(data_path)[-50:]}</div>"

        return html_text

    def get_data_path(self, property_to_load: str):

        data_path = self.data_paths.get(property_to_load)

        if data_path is None:
            raise ValueError(f"No data_path found for property {property_to_load}")
        else:
            return data_path

class Experiment:

    def __init__(self, data_paths: dict, session_type: Session):

        self.data_paths = data_paths
        self.session_type = session_type

    def __iter__(self):
        """Iterate through all items exactly 3 levels deep in the nested dict"""
        for level1_key, level1_value in self.data_paths.items():
            if isinstance(level1_value, dict):
                for level2_key, level2_value in level1_value.items():
                    if isinstance(level2_value, dict):
                        for level3_key, level3_value in level2_value.items():
                            yield self.session_type(level3_value)

    def load_session(self, mouse, day, session):

        mouse_dict = self.data_paths.get(mouse)
        if mouse_dict is None:
             raise ValueError(f"No mouse called {mouse}. Possible mice are {self.data_paths.keys()}.")
        else:
             day_dict = mouse_dict.get(day)
             if day_dict is None:
                 raise ValueError(f"No day called {day}. Possible mice are {mouse_dict.keys()}.")
             else:
                  session_dict = day_dict.get(session)
                  if session_dict is None:
                      raise ValueError(f"No session called {session}. Possible mice are {day_dict.keys()}.")
                  else:
                    return self.session_type(session_dict)
                  

                 
    
    def _repr_html_(self):

        html_text = "<div>"
        for mouse, mouse_dict in self.data_paths.items():
            html_text += "<details>"
            html_text += f"<summary>{mouse}</summary>"
            for day, day_dict in mouse_dict.items():
                html_text += "<details style='padding-left:10px'>"
                html_text += f"<summary>{day}</summary>"
                for session, session_info in day_dict.items():
                        html_text += "<details style='padding-left:10px'>"
                        html_text += f"<summary>{session}</summary>"
                        for data_name, data_path in session_info.items():
                            html_text += f"<div style='padding-left:10px'><strong>{data_name}</strong>: ...{str(data_path)[-50:]}</div>"
                        html_text += "</details>"


                html_text += "</details>"
            html_text += "</details>"

        html_text += "</div>"

        return html_text
             
