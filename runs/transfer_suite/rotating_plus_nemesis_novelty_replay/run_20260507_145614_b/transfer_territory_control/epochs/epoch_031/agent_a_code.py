def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if targets:
        tx, ty = min(targets, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), abs(c[0] - ox) + abs(c[1] - oy)))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = -abs(nx - tx) - abs(ny - ty) + 0.01 * (abs(nx - ox) + abs(ny - oy))
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            best = (dx, dy)
            bestv = v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]