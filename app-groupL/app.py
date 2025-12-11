from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# DATABASE CONNECTION
DB_PATH = 'hotel_last_resort.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us treat rows like dicts
    return conn

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    if conn is None:
        return [] if not one else None
    try:
        cursor = conn.cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
        # Convert Row objects to dictionaries
        dict_results = [dict(row) for row in results]
        return (dict_results[0] if dict_results else None) if one else dict_results
    except sqlite3.Error as e:
        print(f"Query error: {e}")
        return [] if not one else None
    finally:
        conn.close()



# CUSTOMER ROUTES
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/account')
def account():
    # Query 5: Revenue by customer (billing totals)
    reservations = query_db('''
        SELECT c.customerId,
        c.lastName AS last_name,
        c.firstName AS first_name,
        COUNT(*) AS bills,
        SUM(b.totalAmount) AS total_billed
        FROM billing AS b
        JOIN customer AS c ON c.customerId = b.customerId
        GROUP BY c.customerId, c.lastName, c.firstName
        ORDER BY total_billed DESC
    ''')
    return render_template('account.html', reservations=reservations)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/guest_rooms')
def guest_rooms():
    # Query available sleeping rooms (not meeting spaces)
    available_rooms = query_db('''
        SELECT rm.roomId, rm.roomNumber, b.buildingName, rt.roomType, bt.bedType,
               rm.squareFootage, rm.hasPaidBar, rs.status AS room_status
        FROM room AS rm
        JOIN building AS b ON b.buildingId = rm.buildingId
        JOIN room_type AS rt ON rt.roomTypeId = rm.roomTypeId
        LEFT JOIN bed_type AS bt ON bt.bedTypeId = rm.bedTypeId
        JOIN room_status AS rs ON rs.roomStatusId = rm.roomStatusId
        LEFT JOIN meeting_space AS ms ON ms.roomId = rm.roomId
        WHERE ms.roomId IS NULL AND rs.status = 'available'
        ORDER BY b.buildingName, rm.roomNumber
    ''')
    total_rooms = len(available_rooms) if available_rooms else 0
    return render_template('guest_rooms.html', available_rooms=available_rooms, total_rooms=total_rooms)

@app.route('/meeting_spaces')
def meeting_spaces_page():
    # Query meeting spaces with amenities
    meeting_spaces = query_db('''
        SELECT ms.roomId, rm.roomNumber, b.buildingName, ms.spaceType, ms.capacity,
               ms.hasProjector, ms.hasWhiteboard, ms.hasPaidBar
        FROM meeting_space AS ms
        JOIN room AS rm ON rm.roomId = ms.roomId
        JOIN building AS b ON b.buildingId = rm.buildingId
        ORDER BY ms.spaceType, rm.roomNumber
    ''')
    total_spaces = len(meeting_spaces) if meeting_spaces else 0
    return render_template('meeting_spaces.html', meeting_spaces=meeting_spaces, total_spaces=total_spaces)

@app.route('/my_reservations')
def my_reservations():
    # Query 1: Reservations per day (by check-in date) - limited to 10
    reservations = query_db('''
        SELECT
        date(r.startDateTime) AS day,
        COUNT(*) AS num_reservations
        FROM reservation AS r
        GROUP BY date(r.startDateTime)
        ORDER BY day DESC
        LIMIT 10
    ''')
    total_reservations = len(reservations) if reservations else 0
    return render_template('my_reservations.html', reservations=reservations, total_reservations=total_reservations)

@app.route('/book')
def book():
    # Get room types for dropdown (both sleeping rooms and meeting spaces)
    room_types = query_db('''
        SELECT DISTINCT rt.roomType, 'room' AS type_category
        FROM room_type AS rt
        ORDER BY rt.roomType
    ''')
    meeting_space_types = query_db('''
        SELECT DISTINCT ms.spaceType AS roomType, 'meeting' AS type_category
        FROM meeting_space AS ms
        ORDER BY ms.spaceType
    ''')
    # Combine both lists
    all_types = room_types + meeting_space_types
    return render_template('book.html', all_types=all_types)

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')


# ============================================
# MANAGEMENT ROUTES
# ============================================

@app.route('/management')
def management_login():
    return render_template('management_login.html')

@app.route('/staff_roster')
def staff_roster():
    # Query staff list with their information
    staff = query_db('''
        SELECT s.staffId, s.firstName, s.lastName, s.email, s.phone,
               s.role, s.department, s.hireDate, s.isActive
        FROM staff AS s
        ORDER BY s.department, s.lastName, s.firstName
    ''')
    # Calculate statistics
    total_staff = len(staff) if staff else 0
    active_staff = len([s for s in staff if s.get('isActive')]) if staff else 0
    return render_template('staff_roster.html', staff=staff, total_staff=total_staff, active_staff=active_staff)

@app.route('/card_management')
def card_management():
    # Query 8: Staff door-reader swipes by department and reader location
    staff_cards = query_db('''
        SELECT s.department, rd.location,
        COUNT(*) AS staff_swipes
        FROM reading_info AS ri
        JOIN staff_card_assignment AS sca ON sca.staffcardId = ri.staffcardId
        JOIN staff AS s ON s.staffId = sca.staffId
        JOIN readers AS rd ON rd.readersId = ri.readerID
        GROUP BY s.department, rd.location
        ORDER BY staff_swipes DESC
    ''')
    # Calculate statistics
    total_swipes = sum(s.get('staff_swipes', 0) for s in staff_cards) if staff_cards else 0
    departments = len(set(s.get('department') for s in staff_cards if s.get('department'))) if staff_cards else 0
    locations = len(set(s.get('location') for s in staff_cards if s.get('location'))) if staff_cards else 0
    return render_template('card_management.html', staff_cards=staff_cards, 
                          total_swipes=total_swipes, departments=departments, locations=locations)


# ============================================
# EMPLOYEE ROUTES
# ============================================

@app.route('/employee')
def employee_login():
    return render_template('employee_login.html')

@app.route('/employee/rooms')
def employee_rooms():
    # Query 7: Open customer requests by request type
    forum_posts = query_db('''
        SELECT cr.depositStatus,
        COUNT(*) AS open_requests
        FROM customer_requests AS cr
        WHERE cr.resolved = 'N'
        GROUP BY cr.depositStatus
        ORDER BY open_requests DESC
    ''')
    # Query 3: Average stay length by room type
    room_types = query_db('''
        SELECT rt.roomType,
        AVG(julianday(r.endDateTime) - julianday(r.startDateTime)) AS avg_nights,
        COUNT(*) AS num_room_bookings
        FROM room_type AS rt
        JOIN room AS rm ON rm.roomTypeId = rt.roomTypeId
        JOIN reservation_room AS rr ON rr.roomId = rm.roomId
        JOIN reservation AS r ON r.reservationId = rr.reservationId
        GROUP BY rt.roomType
        ORDER BY avg_nights DESC
    ''')
    # Query 6: Meeting-space events by space type
    meeting_spaces_events = query_db('''
        SELECT ms.spaceType,
        COUNT(DISTINCT er.eventId) AS events_count
        FROM meeting_space AS ms
        LEFT JOIN reservation_room AS rr ON rr.roomId = ms.roomId
        LEFT JOIN event_reservation AS er ON er.reservationId = rr.reservationId
        LEFT JOIN event AS e ON e.eventId = er.eventId
        GROUP BY ms.spaceType
        ORDER BY ms.spaceType
    ''')
    # Calculate statistics
    total_requests = sum(f.get('open_requests', 0) for f in forum_posts) if forum_posts else 0
    total_bookings = sum(r.get('num_room_bookings', 0) for r in room_types) if room_types else 0
    total_events = sum(m.get('events_count', 0) for m in meeting_spaces_events) if meeting_spaces_events else 0
    return render_template('employee_rooms.html', forum_posts=forum_posts, room_types=room_types, 
                          meeting_spaces_events=meeting_spaces_events, total_requests=total_requests, 
                          total_bookings=total_bookings, total_events=total_events)

@app.route('/employee/customer_cards')
def employee_customer_cards():
    # Query 5: Revenue by customer (billing totals)
    customer_cards = query_db('''
        SELECT c.customerId,
        c.lastName AS last_name,
        c.firstName AS first_name,
        COUNT(*) AS bills,
        SUM(b.totalAmount) AS total_billed
        FROM billing AS b
        JOIN customer AS c ON c.customerId = b.customerId
        GROUP BY c.customerId, c.lastName, c.firstName
        ORDER BY total_billed DESC
    ''')
    total_customers = len(customer_cards) if customer_cards else 0
    total_revenue = sum(c.get('total_billed', 0) for c in customer_cards) if customer_cards else 0
    return render_template('employee_customer_cards.html', customer_cards=customer_cards, 
                          total_customers=total_customers, total_revenue=total_revenue)

@app.route('/employee/room_list')
def employee_room_list():
    # Query 2: Room counts by status for each building
    rooms = query_db('''
        SELECT b.buildingName,
        rs.status AS room_status,
        COUNT(*) AS num_rooms
        FROM building AS b
        JOIN room AS rm ON rm.buildingId = b.buildingId
        JOIN room_status AS rs ON rs.roomStatusId = rm.roomStatusId
        GROUP BY b.buildingName, rs.status
        ORDER BY b.buildingName, num_rooms DESC
    ''')
    total_rooms = sum(r.get('num_rooms', 0) for r in rooms) if rooms else 0
    available_rooms = sum(r.get('num_rooms', 0) for r in rooms if r.get('room_status') == 'available') if rooms else 0
    return render_template('employee_room_list.html', rooms=rooms, total_rooms=total_rooms, available_rooms=available_rooms)

@app.route('/employee/reservations')
def employee_reservations_page():
    # Query 1: Reservations per day (by check-in date)
    reservations = query_db('''
        SELECT
        date(r.startDateTime) AS day,
        COUNT(*) AS num_reservations
        FROM reservation AS r
        GROUP BY date(r.startDateTime)
        ORDER BY day
    ''')
    total_reservations = sum(r.get('num_reservations', 0) for r in reservations) if reservations else 0
    total_days = len(reservations) if reservations else 0
    avg_per_day = total_reservations / total_days if total_days > 0 else 0
    return render_template('employee_reservations.html', reservations=reservations, 
                          total_reservations=total_reservations, total_days=total_days, avg_per_day=avg_per_day)

@app.route('/employee/revenue')
def employee_revenue():
    # Query 4: Monthly revenue from transactions
    revenue = query_db('''
        SELECT
        CAST(strftime('%%Y', t.transactionDate) AS INTEGER) AS yr,
        CAST(strftime('%%m', t.transactionDate) AS INTEGER) AS mo,
        SUM(t.amount) AS total_revenue,
        COUNT(*) AS num_tx
        FROM transaction AS t
        GROUP BY strftime('%%Y', t.transactionDate), strftime('%%m', t.transactionDate)
        ORDER BY yr, mo
    ''')
    total_revenue = sum(r.get('total_revenue', 0) for r in revenue) if revenue else 0
    total_transactions = sum(r.get('num_tx', 0) for r in revenue) if revenue else 0
    months_tracked = len(revenue) if revenue else 0
    return render_template('employee_revenue.html', revenue=revenue, 
                          total_revenue=total_revenue, total_transactions=total_transactions, months_tracked=months_tracked)

@app.route('/employee/rooms_never_reserved')
def rooms_never_reserved():
    # Query 9: Rooms that have never been reserved
    rooms = query_db('''
        SELECT b.buildingName, rm.roomNumber
        FROM building AS b
        JOIN room AS rm ON rm.buildingId = b.buildingId
        LEFT JOIN reservation_room AS rr ON rr.roomId = rm.roomId
        WHERE rr.roomId IS NULL
        ORDER BY b.buildingName, rm.roomNumber
    ''')
    total_unused = len(rooms) if rooms else 0
    return render_template('rooms_never_reserved.html', rooms=rooms, total_unused=total_unused)


@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
