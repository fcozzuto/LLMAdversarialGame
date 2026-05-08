def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    best_target = None
    best_d = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        d = abs(rx - sx) + abs(ry - sy)
        if best_d is None or d < best_d:
            best_d = d
            best_target = (rx, ry)

    targets = [best_target] if best_target is not None else [(ox, oy)]
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_for(nx, ny):
        tx, ty = targets[0]
        return abs(tx - nx) + abs(ty - ny)

    chosen = None
    chosen_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = score_for(nx, ny)
        if chosen_val is None or val < chosen_val or (val == chosen_val and (dx, dy) < chosen):
            chosen_val = val
            chosen = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [chosen[0], chosen[1]]