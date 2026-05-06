def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                d1 = md(sx, sy, rx, ry)
                d2 = md(ox, oy, rx, ry)
                targets.append((d1 - d2, d1, rx, ry))
    targets.sort()

    if targets:
        _, _, tx, ty = targets[0]
    else:
        tx, ty = ox, oy

    best = None
    best_pos = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                score = md(nx, ny, tx, ty)
                if best is None or score < best or (score == best and (dx, dy) < best_pos):
                    best = score
                    best_pos = (dx, dy)

    if best_pos is None:
        return [0, 0]
    return [best_pos[0], best_pos[1]]