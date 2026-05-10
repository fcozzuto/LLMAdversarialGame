def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    op = observation.get("opponent_position")
    ox, oy = op if op is not None else (sx, sy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_cell(x, y, tx, ty):
        d = abs(x - tx) + abs(y - ty)
        adj_pen = (0 if abs(x - ox) + abs(y - oy) > 1 else 8)
        obs_pen = (1000000 if (x, y) in obstacles else 0)
        return obs_pen + d + adj_pen

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = (w // 2, h // 2)

    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny, tx, ty)
        if best_sc is None or sc < best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]