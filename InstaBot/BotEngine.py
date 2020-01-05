import AccountAgent, DBUsers
import Constants
import datetime


def init(webdriver):
	Constants.init()
	AccountAgent.login(webdriver)

def update(webdriver):
	# засекание времени
	start = datetime.datetime.now()
	# перед началом, проверка если есть от кого отписаться
	_check_follow_list(webdriver)
	while True:
		# начало подписывания
		AccountAgent.follow_people(webdriver)
		# получить время окончания
		end = datetime.datetime.now()
		# сколько затрачено было времени?
		elapsed = end - start
		# если больше константы то проверить подписчиков
		if elapsed.total_seconds() >= Constants.CHECK_FOLLOWERS_EVERY:
			# сброс старта
			start = datetime.datetime.now()
			# проверка подписчиков
			_check_follow_list(webdriver)


def _check_follow_list(webdriver):
	print("Checking for users to unfollow")
	# получить список для отписки
	users = DBUsers.check_unfollow_list()
	# если есть польз. в списке начать отписывание
	if len(users) > 0:
		AccountAgent.unfollow_people(webdriver, users)