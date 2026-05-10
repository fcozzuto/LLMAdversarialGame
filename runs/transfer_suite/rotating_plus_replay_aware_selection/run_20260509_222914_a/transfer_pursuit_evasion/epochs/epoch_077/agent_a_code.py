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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuit" in role)
    if not (is_evader or is_pursuer):
        is_evader = False
        is_pursuer = True

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    if is_pursuer:
        if resources:
            best_val = None
            best_d = None
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                dres = min(md(nx, ny, rx, ry) for rx, ry in resources)
                dop = md(nx, ny, ox, oy)
                val = (dres, dop)
                if best_val is None or val < best_val:
                    best_val, best_d, best_move = val, dres, (dx, dy)
        else:
            best_val = None
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                dop = md(nx, ny, ox, oy)
                if best_val is None or dop < best_val:
                    best_val, best_move = dop, (dx, dy)
    else:
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            dop = md(nx, ny, ox, oy)
            dres = min((md(nx, ny, rx, ry) for rx, ry in resources), default=0)
            val = (-dop, dres)
            if best_val is None or val < best_val:
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]