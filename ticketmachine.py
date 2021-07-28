from objects import Ticket
import discord

class Ticketmachine:
    def __init__(self):
        self._queue = []  # Tickets in queue
        self._items = []  # All tickets
        self._staffmembers = []

    def create_ticket(self, user: discord.Member):
        # Generate a new ticketnumber
        if len(self._items) == 0:
            tn = 1111111
        else:
            tn = self._items[-1].ticketnumber + 1
        # Create Ticket
        ticket = Ticket(tn, user)
        self._queue.append(ticket)
        self._items.append(ticket)
        place_in_queue = len(self._queue)
        return (ticket.ticketnumber, place_in_queue)
    
    def handle_ticket(self, staffid):
        # Check if there are tickets
        if len(self._queue) == 0:
            print(self._queue)
            return None
        # Assign the question
        ticket = self._queue.pop(0)
        ticket.assign(staffid)
        return (ticket.ticketnumber, ticket.user)

    def finish_ticket(self, ticketnumber: int, messages: list):
        # Find the ticket
        ticket = self.__get_ticket(ticketnumber)
        if ticket == None: return False
        # Check if it being handled
        if ticket.status != 'Handling':
            return False
        # Close the ticket and save the messages
        ticket.close()
        ticket.questions = messages
        return (ticket.user, ticket.staffmember)
    
    def information_ticket(self, ticketnumber: int):
        # Find the ticket
        ticket = self.__get_ticket(ticketnumber)
        if ticket == None: return None
        # Return all the information of the ticketnumber
        return {'user' : ticket.user, 'staff' : ticket.staffmember, 'status' : ticket.status, 'date' : ticket.date, 'duration' : ticket.duration, 'questions' : ticket.questions}
    
    def add_staff(self, staffid: discord.Member):
        if not staffid in self._staffmembers:
            self._staffmembers.append(staffid)
            
    def delete_staff(self, staffid: discord.Member):
        if staffid in self._staffmembers:
            self._staffmembers.remove(staffid)
    
    def already_in_queue(self, user: discord.Member):
        current_ticket = None
        for ticket in self._queue:
            if user == ticket.userid:
                current_ticket = ticket
                break
        if current_ticket == None: return None
        return (current_ticket.ticketnumber, self._queue.index(current_ticket) + 1)
    
    def history(self, user: discord.Member):
        hist = []
        for ticket in self._items:
            if ticket.user == user:
                hist.append(ticket.ticketnumber)
        return hist
    
    @property
    def isEmpty(self):
        return self._queue == []
    @property
    def size(self):
        return len(self._queue)
    @property
    def list(self):
        return self._queue
    
    def __get_ticket(self, ticketnumber: int):
        # Find the ticket
        ticket = None
        for t in self._items:
            if t.ticketnumber == ticketnumber:
                ticket = t
        return ticket
    
    
    
