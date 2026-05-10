def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except:
            pass

    resources = []
    for t in observation.get("resources") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resources = resources[:12]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        # Evaluate by best target among a small subset.
        cur_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if sd == 0:
                val = 10**9
            else:
                center = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
                val = (od - sd) * 1000 - sd * 3 + center
            if val > cur_best:
                cur_best = val

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then larger cur_best already.
        if cur_best > best_val or (cur_best == best_val and (dx, dy) < best_move):
            best_val = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]