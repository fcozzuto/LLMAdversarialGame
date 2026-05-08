def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) and ("pursuer" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny)
        mob = mobility(nx, ny)
        # pursuer: smaller d better; evader: larger d better
        primary = -d if evader else d
        secondary = -mob
        # deterministic tie-break: prefer (0,0), then order by dx,dy
        stay_bonus = 0 if (dx == 0 and dy == 0) else 1
        key = (primary, secondary, stay_bonus, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]