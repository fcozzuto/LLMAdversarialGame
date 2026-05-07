def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not isinstance(w, int):
        try:
            w = int(w)
        except:
            w = 0
    if not isinstance(h, int):
        try:
            h = int(h)
        except:
            h = 0
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy = int(sx), int(sy)
        ox, oy = int(ox), int(oy)
    except:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def king(x1, y1, x2, y2):
        d = abs(x2 - x1)
        e = abs(y2 - y1)
        return d if d >= e else e

    def best_move_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for mdx, mdy in cand:
            nx, ny = sx + mdx, sy + mdy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [mdx, mdy]
        return [0, 0]

    if not resources:
        return best_move_towards(ox, oy)

    def move_value(nsx, nsy):
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = king(nsx, nsy, rx, ry)
            od = king(ox, oy, rx, ry)
            if sd == 0:
                val = 10**9
            else:
                val = (od - sd) * 1000 - sd
            if val > best:
                best = val
        if best == -10**18:
            best = -king(nsx, nsy, ox, oy)
        return best

    best = -10**18
    best_pair = (0, 0)
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not (0 <= nsx < w and 0 <= nsy < h):
            continue
        if (nsx, nsy) in obstacles:
            continue
        v = move_value(nsx, nsy)
        if v > best:
            best = v
            best_pair = (mdx, mdy)

    return [int(best_pair[0]), int(best_pair[1])]