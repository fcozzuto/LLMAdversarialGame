def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    r = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in r) or ("chaser" in r)

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = None
    # Deterministic tie-break order: prefer staying put, then N/E/S/W, then diagonals
    move_pref = {(0, 0): 0, (0, -1): 1, (1, 0): 2, (0, 1): 3, (-1, 0): 4,
                 (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8, (-1, 1): 7, (1, -1): 6}
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = manhattan(nx, ny, ox, oy)
        # Small heuristic to avoid corners blocked by obstacles
        wall_pen = 0
        if not inside(nx + 1, ny): wall_pen += 1
        if not inside(nx - 1, ny): wall_pen += 1
        if not inside(nx, ny + 1): wall_pen += 1
        if not inside(nx, ny - 1): wall_pen += 1

        if is_pursuer:
            val = (-d, wall_pen, move_pref.get((dx, dy), 9))
        else:
            # Evader tries to maximize distance; also slightly prefer moves that reduce "wall_pen" (more maneuverability)
            val = (d, -wall_pen, move_pref.get((dx, dy), 9))

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]