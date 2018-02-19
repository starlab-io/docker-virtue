class EventParser(object):

	def parse(self, msg):
		msg['EVENT'] = msg['MESSAGE'].split()[0]
		return True


if __name__ == '__main__':
	parser = EventParser()
	msg = {}
	msg['MESSAGE'] = "first one:ONE two:TWO"
	print parser.parse(msg)
	print msg	