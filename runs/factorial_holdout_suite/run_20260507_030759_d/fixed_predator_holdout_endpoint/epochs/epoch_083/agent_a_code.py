def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try: w = int(w)
    except: w = 8
    try: h = int(h)
    except: h = 8

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            try: return int(v[0]), int(v[1])
            except: return 0, 0
        return 0, 0

    sx, sy = to_xy(observation.get("self_position") or [0, 0])
    ox, oy = to_xy(observation.get("opponent_position") or [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_cells(v):
        out = []
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                except:
                    continue
                if inb(x, y):
                    out.append((x, y))
        return out

    obstacles = set(parse_cells(observation.get("obstacles")))
    resources = [p for p in parse_cells(observation.get("resources")) if p not in obstacles]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_adv = None
        for rx, ry in resources:
            own_d = abs(nx - rx)
            od_d = abs(ny - ry)
            if od_d > own_d: own_d = od_d  # Chebyshev distance
            opp_d = abs(ox - rx)
            t = abs(oy - ry)
            if t > opp_d: opp_d = t
            adv = opp_d - own_d
            if best_adv is None or adv > best_adv:
                best_adv = adv
        if best_adv is None:
            continue
        cand = (best_adv, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]