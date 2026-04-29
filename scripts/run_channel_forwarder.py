from src.integrations.telegram.channel_forwarder import main, client


if __name__ == "__main__":
    client.loop.run_until_complete(main())
