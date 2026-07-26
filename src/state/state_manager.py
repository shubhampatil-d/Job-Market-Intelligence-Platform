from pathlib import Path
import json
from datetime import datetime


class PipelineStateManager:

    def __init__(self):

        self.state_file = Path("state/pipeline_state.json")

        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


    def default_state(self):

        return {

            "last_run": None,

            "last_cursor": None,

            "records_processed": 0,

            "pipeline_version": "1.0",

            "status": "NEVER_RUN",
        }


    def load(self):

        if not self.state_file.exists():

            return self.default_state()

        with open(
            self.state_file,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)


    def save(
        self,
        cursor,
        records_processed,
    ):

        state = {

            "last_run": datetime.utcnow().isoformat(),

            "last_cursor": cursor,

            "records_processed": records_processed,

            "pipeline_version": "1.0",

            "status": "SUCCESS",
        }

        with open(
            self.state_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                state,
                file,
                indent=4,
            )