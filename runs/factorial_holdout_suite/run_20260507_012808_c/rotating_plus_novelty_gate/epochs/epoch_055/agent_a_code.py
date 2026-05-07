def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0) or 8
    h = int(observation.get("grid_height", 0) or 0) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except:
            pass

    res = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
        except:
            pass

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if res:
        target = min(res, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
        tx, ty = target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -dist((nx, ny), (tx, ty))
            # tie-break deterministically by moving away from opponent
            score2 = abs(nx - ox) + abs(ny - oy)
            t = (score, score2)
            if best is None or t > best_score:
                best_score = t
                best = [dx, dy]
    else:
        # no resources: move to increase distance from opponent
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = abs(nx - ox) + abs(ny - oy)
            t = (score, -(abs(dx) + abs(dy)), nx, ny)
            if best is None or t > best_score:
                best_score = t
                best = [dx, dy]

    return best if best is not None else [0, 0]