def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    if w <= 0 or h <= 0:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if not res:
        dxs = [0, 1, -1]
        best = (None, -10**18)
        for dx in dxs:
            for dy in dxs:
                nx, ny = sx + dx, sy + dy
                if (dx, dy) == (0, 0):
                    continue
                if not in_bounds(nx, ny) or (nx, ny) in obs:
                    continue
                val = -dist2(nx, ny, ox, oy)
                if val > best[1]:
                    best = ((dx, dy), val)
        return [0, 0] if best[0] is None else [best[0][0], best[0][1]]

    target = res[0]
    best_t = dist2(sx, sy, target[0], target[1])
    for r in res[1:]:
        d = dist2(sx, sy, r[0], r[1])
        if d < best_t:
            best_t = d
            target = r

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        my_d = dist2(nx, ny, tx, ty)
        opp_d = dist2(ox, oy, tx, ty)
        val = (opp_d - my_d)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]