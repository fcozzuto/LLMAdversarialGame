def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try:
                return int(v[0]), int(v[1])
            except:
                return 0, 0
        return 0, 0

    sx, sy = to_xy(observation.get("self_position", (0, 0)))
    ox, oy = to_xy(observation.get("opponent_position", (0, 0)))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for rx, ry in resources:
        myd = abs(sx - rx) + abs(sy - ry)
        opd = abs(ox - rx) + abs(oy - ry)
        steal = -1000 if (rx, ry) == (observation.get("scores") or {}).get("opponent_target", (rx, ry)) else 0
        key = (myd - opd + steal, myd, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_step = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
            d = abs(nx - tx) + abs(ny - ty)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_step):
                best_d = d
                best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]