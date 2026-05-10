def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref_order = {
        (0, 0): 0, (0, -1): 1, (1, 0): 2, (0, 1): 3, (-1, 0): 4,
        (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8
    }

    r = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r)
    sign = -1 if pursuer else 1

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def bfs_dist(startx, starty, limit=14):
        if (startx, starty) == (ox, oy):
            return 0
        qx, qy = [startx], [starty]
        dist = {(startx, starty): 0}
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            d = dist[(x, y)]
            if d >= limit:
                continue
            nd = d + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not legal(nx, ny):
                    continue
                if (nx, ny) in dist:
                    continue
                if (nx, ny) == (ox, oy):
                    return nd
                dist[(nx, ny)] = nd
                qx.append(nx)
                qy.append(ny)
        return None

    best = None
    best_move = [0, 0]
    cur_d = manhattan(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md = bfs_dist(nx, ny, limit=14)
        dman = manhattan(nx, ny, ox, oy)
        # pursuer: minimize path length; evader: maximize it
        if md is None:
            md = 99
        # tie-break favors closer corners/opponent-facing progress deterministically
        corner_bias = manhattan(nx, ny, 0, 0) + 0.3 * manhattan(nx, ny, w - 1, h - 1)
        score = sign * (md * 2.0 + dman) + (0.05 if sign == -1 else -0.05) * corner_bias
        # small improvement pressure to not stall
        score += sign * 0.01 * (dman - cur_d)
        key = (score, -pref_order[(dx, dy)])
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    return best_move