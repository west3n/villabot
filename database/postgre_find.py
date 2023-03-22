from database.postgre import cur, db
import re
from database.postgre_user import status


def check_budget(currency_str, budget_str):
    try:
        if currency_str == 'usd':
            if 'less than 650$' in budget_str:
                budget_str = budget_str.replace('less than 650$', '0 - 650$')
            if 'more than 3250$' in budget_str:
                budget_str = budget_str.replace('more than 3250$', '3250 - 1000000$')
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
    locations = location_str.split(',')
    locations = [loc.strip() for loc in locations]
    placeholders = ','.join(['%s'] * len(locations))
    cur.execute(f"SELECT id FROM appart_location WHERE name IN ({placeholders})", tuple(locations))
    result = cur.fetchall()
    return [int(x[0]) for x in result]


def get_all_locations():
    cur.execute("SELECT id FROM appart_location")
    result = cur.fetchall()
    return [int(x[0]) for x in result]


def get_location_name(location_id):
    cur.execute(f"SELECT name FROM appart_location WHERE id=%s", (location_id,))
    result = cur.fetchone()
    return result


def get_apart(rental_period_str, currency_str, budget_str, location_str, accommodation_type_str, amenities_str):
    budget = check_budget(currency_str, budget_str)
    aps_type = type_check(accommodation_type_str)
    aps_type = aps_type.split(',')
    aps_type = [loc.strip() for loc in aps_type]
    aps_hold = ','.join(['%s'] * len(aps_type))
    location_id = get_location_id(location_str)
    location_hold = ','.join(['%s'] * len(location_id))
    amenities = amenities_str.split(',')
    amenities = [amenity.strip() for amenity in amenities]
    cur.execute("SELECT id FROM appart_apartment")
    count = len(cur.fetchall())
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
        matching_aps = []
        for n in range(0, count):
            compare = all(element in aps[n][6].split(",") for element in amenities)
            if compare:
                matching_aps.append(aps[n])
        return matching_aps


def get_image(unique_id):
    cur.execute("SELECT image_id FROM appart_apartment_images WHERE apartment_id=%s", (unique_id,))
    images = cur.fetchall()
    image_link = []
    for image in images:
        cur.execute("SELECT image FROM appart_image WHERE id=%s", (image,))
        image_link.append(cur.fetchone()[0]),
    return image_link


async def get_save_request(user_id):
    cur.execute("SELECT id FROM appart_saverequest WHERE user_id=%s", (user_id,))
    result = cur.fetchone()
    return result


async def save_request(tg_id, rental_period_str, currency_str, budget_str,
                       location_str, accommodation_type_str, amenities_str):
    request = f'{rental_period_str}/{currency_str}/{budget_str}/{location_str}/{accommodation_type_str}/{amenities_str}'
    user_id = await status(tg_id)
    x = await get_save_request(user_id)
    if x:
        cur.execute("UPDATE appart_saverequest SET request=%s WHERE user_id=%s AND id=%s", (request, user_id, x[0]))
        db.commit()
    if x is None:
        cur.execute("INSERT INTO appart_saverequest(user_id, request) VALUES (%s, %s)", (user_id, request))
        db.commit()


async def get_request(tg_id):
    user_id = await status(tg_id)
    cur.execute("SELECT request FROM appart_saverequest WHERE user_id=%s", (user_id,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None
