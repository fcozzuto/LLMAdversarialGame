def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursue = ("pursuer" in role) or ("catch" in role) or ("hunter" in role)

    order = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = None

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oset:
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            val = -d2 if pursue else d2
            if best is None or val > best_val:
                best = [dx, dy]
                best_val = val

    return best if best is not None else [0, 0]