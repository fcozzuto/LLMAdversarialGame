def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_for(nx, ny):
        if is_pursuer:
            primary = -(abs(nx - ox) + abs(ny - oy))
        else:
            primary = (abs(nx - ox) + abs(ny - oy))
        best_res = None
        for r in observation.get("resources") or []:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                d = abs(nx - rx) + abs(ny - ry)
                if best_res is None or d < best_res:
                    best_res = d
        if best_res is None:
            return primary
        return primary - best_res * 0.5

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = score_for(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]