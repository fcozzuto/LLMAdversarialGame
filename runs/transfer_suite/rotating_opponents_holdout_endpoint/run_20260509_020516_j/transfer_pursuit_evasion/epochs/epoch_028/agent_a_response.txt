def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)
    if not i_am_pursuer:
        if ("pursuer" in opp_role) or ("pursuit" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursue" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = True  # fallback

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist(nx, ny, ox, oy)
        cap = 1 if d == 0 else 0
        # obstacle-aware "mobility": count valid neighbors
        mob = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                mob += 1
        candidates.append((cap, d, -mob, nx, ny, dx, dy))

    if i_am_pursuer:
        # minimize distance, prioritize immediate capture, then mobility
        best = min(candidates, key=lambda t: (-t[0], t[1], t[2]))
    else:
        # maximize distance, avoid traps by favoring mobility; if capture possible, avoid it
        best = max(candidates, key=lambda t: (t[0], t[1], t[2]))

    return [int(best[5]), int(best[6])]