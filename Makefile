.PHONY: clean

clean:
	@git clean -f -d -X

pull:
	@git config pull.off only
	@git pull
deploy:
	@docker-compose stop
	@docker-compose up -d --build