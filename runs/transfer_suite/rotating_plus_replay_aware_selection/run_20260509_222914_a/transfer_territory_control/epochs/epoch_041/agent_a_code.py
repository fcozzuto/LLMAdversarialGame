def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def collect(keys):
        out = []
        for k in keys:
            for p in observation.get(k) or []:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = p[0], p[1]
                    if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                        out.append((x, y))
        return out

    unclaimed = collect(["unclaimed_cells", "unclaimed"])
    resources = collect(["resources", "resource_cells", "resource_locations"])
    target_list = unclaimed if unclaimed else resources if resources else []

    tx, ty = ox, oy
    if target_list:
        best = None
        for x, y in target_list:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if best is None or d < best[0] or (d == best[0] and (x, y) < (best[1], best[2])):
                best = (d, x, y)
        tx, ty = best[1], best[2]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score += 0 if (dx, dy) == (0, 0) else 0
        if score < (best_score if best_score is not None else score + 1) or (best_score is None and True):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]