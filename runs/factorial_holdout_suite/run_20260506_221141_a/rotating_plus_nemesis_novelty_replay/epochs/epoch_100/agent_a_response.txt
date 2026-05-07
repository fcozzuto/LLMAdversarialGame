def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position", [0, 0]))
    ox, oy = to_xy(observation.get("opponent_position", [0, 0]))
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

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_r = None
    best_key = None
    for r in resources:
        sd = manh(sx, sy, r[0], r[1])
        od = manh(ox, oy, r[0], r[1])
        gap = od - sd
        key = (gap, -sd, -r[1], -r[0])
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = None
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue
        sd_next = manh(nx, ny, tx, ty)
        od_now = manh(ox, oy, tx, ty)
        gap = od_now - sd_next
        # small preference to reduce distance to target; also avoid getting "stuck" far off
        mkey = (gap, -sd_next, -(abs(nx - tx) + abs(ny - ty)), -nx, -ny)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]