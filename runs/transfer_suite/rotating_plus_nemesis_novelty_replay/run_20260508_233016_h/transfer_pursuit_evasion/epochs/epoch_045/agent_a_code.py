def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursuit" in role)
    if not ("evader" in role) and role == "":
        is_pursuer = True

    cand_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)
        boundary = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        # pursuer: minimize distance; evader: maximize distance; slight bias to stay central
        if is_pursuer:
            val = dist * 1000 + int(boundary * 3)
            better = (best is None) or (val < best[0])
        else:
            val = -dist * 1000 + int(boundary * 3)
            better = (best is None) or (val > best[0])
        if better:
            best = (val, dx, dy)

    if best is None:
        # If all moves blocked, try staying or any valid neighbor
        if inb(sx, sy):
            return [0, 0]
        for dx, dy in cand_dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]