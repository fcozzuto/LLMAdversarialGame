def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a "flee" corner deterministically: farthest from opponent, with obstacle tiebreak.
    best_corner = None
    best_corner_key = None
    for c in corners:
        if c in obstacles:
            continue
        cx, cy = c
        key = (cheb(cx, cy, ox, oy), -(cx + cy), cx, cy)
        if best_corner_key is None or key > best_corner_key:
            best_corner_key = key
            best_corner = c
    if best_corner is None:
        best_corner = (0, 0)

    role = (observation.get("self_role") or "").lower()

    # Threatenedness proxy: how close destination is to opponent relative to current.
    cur_d = cheb(sx, sy, ox, oy)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        corner_dist = cheb(nx, ny, best_corner[0], best_corner[1])

        # Small obstacle-avoidance: penalize stepping near obstacles (in Chebyshev).
        near_obs = 10
        for (oxb, oyb) in obstacles:
            t = cheb(nx, ny, oxb, oyb)
            if t < near_obs:
                near_obs = t

        if role == "pursuer":
            # Pursuit: minimize distance; also avoid obstacles; deterministic tie-break.
            key = (-d, corner_dist, near_obs, nx + ny, nx, ny)
        else:
            # Evasion: maximize distance; also head toward chosen corner (not necessarily absolute max every step).
            improve = d - cur_d
            key = (d, improve, corner_dist * -1, near_obs, -(nx + ny), nx, ny)

        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]