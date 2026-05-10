def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer and (("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role)):
        i_am_pursuer = False
    elif not i_am_pursuer:
        i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def deg_blocked(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                c += 1
        return c

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_key = None
    if i_am_pursuer:
        # Direct pursuit with obstacle-aware "avoid dead-ends" tie-breaking
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            cheb = max(abs(nx - ox), abs(ny - oy))
            blocked = deg_blocked(nx, ny)
            key = (d, cheb, blocked, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        if best is None:
            return [0, 0]
        return best
    else:
        # Evader: maximize distance; also prefer safer mobility (avoid being boxed)
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            blocked = deg_blocked(nx, ny)
            cheb = max(abs(nx - ox), abs(ny - oy))
            key = (-d, cheb, -blocked, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        if best is None:
            return [0, 0]
        return best