def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y, pts):
        if not pts:
            return 10**9
        d = 10**9
        for px, py in pts:
            dd = cheb(x, y, px, py)
            if dd < d:
                d = dd
        return d

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    my_near = nearest_dist(sx, sy, resources)
    opp_near = nearest_dist(ox, oy, resources)

    best = None
    # deterministic tiebreak order by (dx,dy)
    legal.sort(key=lambda t: (t[0], t[1]))
    for dx, dy, nx, ny in legal:
        # prefer taking a resource immediately if present
        take = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                take = 1
                break
        my_d = nearest_dist(nx, ny, resources)
        # one-step "threat" estimate: how much we push opponent away from their resources
        opp_d_now = opp_near
        # approximate opponent next position by mirroring our move direction relative to them
        mpx, mpy = ox - (nx - sx), oy - (ny - sy)
        if inb(mpx, mpy) and (mpx, mpy) not in obst:
            opp_d_after = nearest_dist(mpx, mpy, resources)
        else:
            # if blocked by obstacle/wall, they likely stay
            opp_d_after = nearest_dist(ox, oy, resources)
        # Score: maximize immediate gains and reduce our distance, while increasing opponent distance
        score = 0
        score += 1000 * take
        score += (my_near - my_d) * 10
        score += (opp_d_after - opp_d_now) * 7
        # also avoid being too close to opponent (reduces collision risk)
        score -= cheb(nx, ny, ox, oy) * 1
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]