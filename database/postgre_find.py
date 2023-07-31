import re
from database.postgre_user import status
import asyncio
from database.postgre import connect


def check_budget(currency_str, budget_str):
    db, cur = connect()
    try:
        if currency_str == 'usd':
            if 'less than 20$' in budget_str:
                budget_str = budget_str.replace('less than 20$', '0 - 20$')
            if 'more than 140$' in budget_str:
                budget_str = budget_str.replace('more than 140$', '140 - 1000000$')
            if 'less than 650$' in budget_str:
                budget_str = budget_str.replace('less than 650$', '0 - 650$')
            if 'more than 3250$' in budget_str:
                budget_str = budget_str.replace('more than 3250$', '3250 - 1000000$')
            if 'less than 8000$' in budget_str:
                budget_str = budget_str.replace('less than 8000$', '0 - 8000$')
            if 'more than 40000$' in budget_str:
                budget_str = budget_str.replace('more than 40000$', '40000 - 1000000000$')
            s = budget_str
            budget = re.findall(r'\d+', s)
            budget = [int(n) for n in budget]
            min_budget = min(budget)
            max_budget = max(budget)
            return min_budget, max_budget
        elif currency_str == 'rupiah':
            if 'less than 10 mln' in budget_str:
                budget_str = budget_str.replace('less than 10 mln', '0 - 10000000')
            if '10 mln - 20 mln' in budget_str:
                budget_str = budget_str.replace('10 mln - 20 mln', '10000000 - 20000000')
            if '20 mln - 30 mln' in budget_str:
                budget_str = budget_str.replace('20 mln - 30 mln', '20000000 - 30000000')
            if '30 mln - 40 mln' in budget_str:
                budget_str = budget_str.replace('30 mln - 40 mln', '30000000 - 40000000')
            if '40 mln - 50 mln' in budget_str:
                budget_str = budget_str.replace('40 mln - 50 mln', '40000000 - 50000000')
            if 'more than 50 mln' in budget_str:
                budget_str = budget_str.replace('more than 50 mln', '50000000 - 1000000000')
            if 'less than 300k' in budget_str:
                budget_str = budget_str.replace('less than 300k', '0 - 300000')
            if '300k - 700k' in budget_str:
                budget_str = budget_str.replace('300k - 700k', '300000 - 700000')
            if '700k - 1 mln' in budget_str:
                budget_str = budget_str.replace('700k - 1 mln', '700000 - 1000000')
            if '1 mln - 1,5 mln' in budget_str:
                budget_str = budget_str.replace('1 mln - 1,5 mln', '1000000 - 1500000')
            if '1,5 mln - 2 mln' in budget_str:
                budget_str = budget_str.replace('1,5 mln - 2 mln', '1500000 - 2000000')
            if 'more than 2 mln' in budget_str:
                budget_str = budget_str.replace('more than 2 mln', '2000000 - 1000000000')
            if 'less than 120 mln' in budget_str:
                budget_str = budget_str.replace('less than 120 mln', '0 - 120000000')
            if '120 mln - 240 mln' in budget_str:
                budget_str = budget_str.replace('120 mln - 240 mln', '120000000 - 240000000')
            if '240 mln - 360 mln' in budget_str:
                budget_str = budget_str.replace('240 mln - 360 mln', '240000000 - 360000000')
            if '360 mln - 480 mln' in budget_str:
                budget_str = budget_str.replace('360 mln - 480 mln', '360000000 - 480000000')
            if '480 mln - 600 mln' in budget_str:
                budget_str = budget_str.replace('480 mln - 600 mln', '480000000 - 600000000')
            if 'More than 600 mln' in budget_str:
                budget_str = budget_str.replace('More than 600 mln', '600000000 - 1000000000')
            s = budget_str
            budget = re.findall(r'\d+', s)
            budget = [int(n) for n in budget]
            min_budget = min(budget)
            max_budget = max(budget)
            return min_budget, max_budget
    except ValueError:
        min_budget = 0
        max_budget = 1000000000000
        return min_budget, max_budget
    finally:
        cur.close()
        db.close()


def type_check(accommodation_type_str):
    if 'Villa Entirely' in accommodation_type_str:
        accommodation_type_str = accommodation_type_str.replace('Villa Entirely', 'VI')
    if 'Room in a shared villa' in accommodation_type_str:
        accommodation_type_str = accommodation_type_str.replace('Room in a shared villa', 'RO')
    if 'Apartment' in accommodation_type_str:
        accommodation_type_str = accommodation_type_str.replace('Apartments', 'AP')
    if 'Guesthouse' in accommodation_type_str:
        accommodation_type_str = accommodation_type_str.replace('Guesthouse', 'GH')
    return accommodation_type_str


def get_location_id(location_str):
    db, cur = connect()
    try:
        locations = location_str.split(',')
        locations = [loc.strip() for loc in locations]
        placeholders = ','.join(['%s'] * len(locations))
        cur.execute(f"SELECT id FROM appart_location WHERE name IN ({placeholders})", tuple(locations))
        result = cur.fetchall()
        return [int(x[0]) for x in result]
    finally:
        db.close()
        cur.close()


def get_all_locations():
    db, cur = connect()
    try:
        cur.execute("SELECT id FROM appart_location")
        result = cur.fetchall()
        return [int(x[0]) for x in result]
    finally:
        db.close()
        cur.close()


def get_location_name(location_id):
    db, cur = connect()
    try:
        cur.execute(f"SELECT name FROM appart_location WHERE id=%s", (location_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


def get_apart(rental_period_str, currency_str, budget_str, location_str, accommodation_type_str, amenities_str):
    db, cur = connect()
    try:
        budget = check_budget(currency_str, budget_str)
        aps_type = type_check(accommodation_type_str)
        aps_type = aps_type.split(',')
        aps_type = [loc.strip() for loc in aps_type]
        aps_hold = ','.join(['%s'] * len(aps_type))
        location_id = get_location_id(location_str)
        location_hold = ','.join(['%s'] * len(location_id))
        amenities = amenities_str.split(',')
        amenities = [amenity.strip() for amenity in amenities]
        count = get_last_id()
        if aps_type == ['']:
            aps_type = ["VI", "RO", "AP", "GH"]
            aps_hold = ','.join(['%s'] * len(aps_type))
        if not location_id:
            location_id = get_all_locations()
            location_hold = ','.join(['%s'] * len(location_id))
        if currency_str == 'usd':
            cur.execute(
                f"SELECT * FROM appart_apartment WHERE rent_term=%s "
                f"AND aps_type IN ({aps_hold}) "
                f"AND location_id IN ({location_hold}) "
                f"AND price_usd BETWEEN %s AND %s",
                (rental_period_str,) + tuple(aps_type + location_id) + (int(budget[0]),) + (
                    int(budget[1]),)
            )
            aps = cur.fetchall()

            return aps

        elif currency_str == 'rupiah':
            cur.execute(
                f"SELECT * FROM appart_apartment WHERE rent_term=%s "
                f"AND aps_type IN ({aps_hold}) "
                f"AND location_id IN ({location_hold}) "
                f"AND price_rup BETWEEN %s AND %s",
                (rental_period_str,) + tuple(aps_type + location_id) + (int(budget[0]),) + (
                    int(budget[1]),)
            )
            aps = cur.fetchall()

            return aps
            # matching_aps = []
            # for n in range(0, count):
            #     compare = all(element in aps[n][6].split(",") for element in amenities)
            #     if compare:
            #         matching_aps.append(aps[n])
            # return matching_aps
    finally:
        db.close()
        cur.close()


def get_image(unique_id):
    db, cur = connect()
    try:
        cur.execute("SELECT image_id FROM appart_apartment_images WHERE apartment_id=%s", (unique_id,))
        images = cur.fetchall()
        image_link = []
        for image in images:
            cur.execute("SELECT image FROM appart_image WHERE id=%s", (image,))
            image_link.append(cur.fetchone()[0]),
        return image_link
    finally:
        db.close()
        cur.close()


async def get_save_request(user_id):
    db, cur = connect()
    try:
        cur.execute("SELECT id FROM appart_saverequest WHERE user_id=%s", (user_id,))
        result = cur.fetchone()
        return result
    finally:
        db.close()
        cur.close()


async def save_request(tg_id, rental_period_str, currency_str, budget_str,
                       location_str, accommodation_type_str, amenities_str):
    db, cur = connect()
    try:
        request = f'{rental_period_str}/{currency_str}/{budget_str}/{location_str}/{accommodation_type_str}/{amenities_str}'
        user_id = await status(tg_id)
        x = await get_save_request(user_id)
        if x:
            cur.execute("UPDATE appart_saverequest SET request=%s WHERE user_id=%s AND id=%s", (request, user_id, x[0]))
            db.commit()
        if x is None:
            cur.execute("INSERT INTO appart_saverequest(user_id, request) VALUES (%s, %s)", (user_id, request))
            db.commit()
    finally:
        db.close()
        cur.close()


async def get_request(tg_id):
    db, cur = connect()
    try:
        user_id = await status(tg_id)
        cur.execute("SELECT request FROM appart_saverequest WHERE user_id=%s", (user_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return None
    finally:
        db.close()
        cur.close()


def get_last_id():
    db, cur = connect()
    try:
        cur.execute("SELECT MAX(id) FROM appart_apartment")
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return 0
    finally:
        db.close()
        cur.close()
