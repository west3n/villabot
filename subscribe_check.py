import asyncio
import datetime

from database import postgre_user


async def main():
    print("Задача по окончанию подписки запущена!")
    while True:
        now = datetime.datetime.now()
        if now.hour == 0 and now.minute == 30:
            all_tg_ids = await postgre_user.get_all_tg_ids()
            for tg_id in all_tg_ids:
                user_data = await postgre_user.get_user_data(tg_id)
                subscription_date = user_data[10]
                if datetime.datetime.now().date() == subscription_date:
                    await postgre_user.end_subscription(tg_id)
                    print(f"Subscription end: {tg_id}")
        await asyncio.sleep(60 - now.second)


if __name__ == '__main__':
    asyncio.run(main())
