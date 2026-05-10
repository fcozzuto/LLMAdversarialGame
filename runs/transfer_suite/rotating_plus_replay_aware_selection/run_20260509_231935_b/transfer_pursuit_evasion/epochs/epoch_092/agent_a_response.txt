def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursu" in self_role) or ("chase" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    pref = [(0,-1), (-1,0), (1,0), (0,1), (-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
    ordered = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    best = None
    best_val = None
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        if is_pursuer:
            val = (d, cheb(nx, ny, 0, 0), cheb(nx, ny, w - 1, h - 1))
            better = best_val is None or val < best_val
        else:
            val = (-d, cheb(nx, ny, 0, 0), cheb(nx, ny, w - 1, h - 1))
            better = best_val is None or val < best_val
        if better:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]

    # If staying still is picked but capture-avoidance allows improvement, nudge deterministically.
    if best == (0, 0):
        alt = None
        alt_val = None
        for dx, dy in ordered:
            if (dx, dy) == (0, 0):
                continue
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if is_pursuer:
                val = (d, dx, dy)
                better = alt_val is None or val < alt_val
            else:
                val = (-d, dx, dy)
                better = alt_val is None or val < alt_val
            if better:
                alt_val = val
                alt = (dx, dy)
        if alt is not None:
            return [int(alt[0]), int(alt[1])]

    return [int(best[0]), int(best[1])]