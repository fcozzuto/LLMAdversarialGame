def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    res = [(int(p[0]), int(p[1])) for p in resources]
    if not res:
        return [0, 0]

    opp_nearest = None
    best_opp_d = 10**9
    for rx, ry in res:
        d = cheb(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            opp_nearest = (rx, ry)

    best_move = (0, 0)
    best_val = -10**18

    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny):
            nx, ny = sx, sy

        nearest_d = 10**9
        good_count = 0
        near_count = 0
        capture = 0

        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self < nearest_d:
                nearest_d = d_self
            if d_self == 0:
                capture += 1
            if d_self <= d_opp:
                good_count += 1
            if d_self <= 2:
                near_count += 1

        if nearest_d == 10**9:
            nearest_term = -1000
        else:
            nearest_term = -nearest_d

        opp_pressure = -cheb(nx, ny, opp_nearest[0], opp_nearest[1]) if opp_nearest else 0
        val = 50 * capture + 3 * good_count + 1.2 * near_count + nearest_term + 0.2 * opp_pressure

        # tie-break: prefer moves that also reduce distance to best resource for self
        if val > best_val:
            best_val = val
            best_move = (dx0, dy0)
        elif val == best_val:
            if cheb(nx, ny, res[0][0], res[0][1]) < cheb(sx, sy, res[0][0], res[0][1]):
                best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]