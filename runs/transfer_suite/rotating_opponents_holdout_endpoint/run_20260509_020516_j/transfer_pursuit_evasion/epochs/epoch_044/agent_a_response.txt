def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    bestv = None
    tieb = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist(nx, ny)
        if is_pursuer:
            v = -d
            tb = d
        else:
            # Evader: maximize distance and also prefer escaping to farthest corner deterministically
            far_corner = max(corners, key=lambda c: dist(c[0], c[1]))
            corner_bonus = dist(nx, ny) + (dist(far_corner[0], far_corner[1]) - dist(ox, oy)) * 0.01
            v = corner_bonus
            tb = -corner_bonus
        if best is None or (v > bestv) or (v == bestv and tb < tieb):
            best, bestv, tieb = (dx, dy), v, tb

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]