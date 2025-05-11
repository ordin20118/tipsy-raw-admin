from raw_data_manager.classes import SearchParam

class SearchLiquorQueryParams(SearchParam):
    def __init__(self, state=None, liquor_id=None):
        self.state = state
        self.liquor_id = liquor_id