def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx >= dy else dy  # turns with 8-neighbor moves

    best_t = resources[0]
    best_key = None
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        key = (do - ds, -ds, -abs(tx - ox) + abs(ty - oy), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)
        # Prefer decreasing our time to target; if tied, deny opponent by keeping them closer disadvantage.
        mkey = (-nd, (od - nd), -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_m_key is None or mkey > best_m_key:
            best_m_key = mkey
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]