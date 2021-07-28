from dataclasses import dataclass
import discord
import datetime

@dataclass
class Ticket:
    ticketnumber: int
    user: discord.Member
    
    def __post_init__(self):
        self.open()
    
    def open(self):
        self.status = 'Open'
        self.date = datetime.datetime.now()
        self.staffmember = None
        self.duration = None
        self.questions = None
    
    def assign(self, staff: discord.Member):
        self.staffmember = staff
        self.status = 'Handling'
    
    def close(self):
        self.status = 'Closed'
        self.duration = datetime.datetime.now() - self.date

        

    
