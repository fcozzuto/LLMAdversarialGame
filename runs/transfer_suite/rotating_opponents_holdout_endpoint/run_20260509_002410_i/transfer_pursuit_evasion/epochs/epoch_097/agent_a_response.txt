def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    eps = 1e-6

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (x + dx, y + dy) in obstacles:
                    n += 1
        return n

    target_dx = ox - sx
    target_dy = oy - sy
    if abs(target_dx) > abs(target_dy):
        pref_x = 1 if target_dx > 0 else -1
        pref_y = 1 if target_dy >= 0 else -1
    else:
        pref_y = 1 if target_dy > 0 else -1
        pref_x = 1 if target_dx >= 0 else -1

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            v = 1e18
        elif (nx, ny) in obstacles:
            v = 1e17
        else:
            d = cheb(nx, ny, ox, oy)
            pobs = near_obs(nx, ny)
            # tie-break: prefer reducing/increasing the dominant direction to avoid loops
            dir_term = (pref_x * (nx - sx)) + (pref_y * (ny - sy))
            if is_pursuer:
                v = d * 1000 + pobs * 10 - dir_term
            else:
                v = (-d) * 1000 - pobs * 10 + dir_term
        if bestv is None or v < bestv - eps:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]