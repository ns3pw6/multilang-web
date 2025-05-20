from .dbModel import Separator

class SeparatorModel(Separator):
    
    def get_sep_type(self, platform_id: int, file_format: str) -> int:
        if platform_id == 1 or (platform_id == 2 and file_format == 'xaml'):
            return 1
        elif platform_id == 8 or platform_id == 9:
            return 3
        else:
            return 2
    
    @classmethod
    def get(cls, sep_id: int) -> str:
        return cls.query.filter_by(sep_id = sep_id).first()
