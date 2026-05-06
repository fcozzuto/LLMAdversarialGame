def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = (sx + ox) // 2, (sy + oy) // 2
    # prefer guard unless opponent has a clear lead on a resource
    best_resource = None
    best_lead = -10**9
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        lead = opp_d - self_d  # positive => we are closer
        # opponent is closer when lead is negative; pick most negative (largest opponent advantage)
        if -lead > best_lead:
            best_lead = -lead
            best_resource = (rx, ry)

    chase_mode = False
    chase_margin = 1  # if opponent is significantly closer, chase
    if best_resource is not None:
        rx, ry = best_resource
        chase_mode = md(ox, oy, rx, ry) + chase_margin < md(sx, sy, rx, ry)

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        # evaluate guard/defend
        guard_score = -md(nx, ny, tx, ty)

        if chase_mode:
            rx, ry = best_resource
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # maximize (our closeness advantage), break ties with being closer
            chase_score = (opp_d - self_d, -self_d)
            key = (1, chase_score, guard_score)
        else:
            # while guarding, avoid moving into opponent-immediate reach of any resource
            min_opp_to_resource = 10**9
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = int(r[0]), int(r[1])
                if valid(rx, ry):
                    min_opp_to_resource = min(min_opp_to_resource, md(ox, oy, rx, ry))
            # prefer moves that increase distance from opponent and keep guard position tight
            opp_dist = md(nx, ny, ox, oy)
            key = (0, (-min_opp_to_resource, opp_dist), guard_score)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move