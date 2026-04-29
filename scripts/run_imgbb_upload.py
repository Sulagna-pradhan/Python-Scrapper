from src.integrations.imgbb_upload import process_channel, client


if __name__ == "__main__":
    target = input("Enter Telegram Channel Username or Link: ").strip()
    local_enabled = input("Enable local download? (yes/no): ").strip().lower() == "yes"
    with client:
        client.loop.run_until_complete(process_channel(target, local_enabled))
