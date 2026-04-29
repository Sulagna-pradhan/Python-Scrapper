from src.integrations.telegram.movie_indexer import main, client


if __name__ == "__main__":
    client.loop.run_until_complete(main())
