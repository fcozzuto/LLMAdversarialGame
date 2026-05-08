def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if w is not None else 8
    h = int(h) if h is not None else 8

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = set()
    uc = observation.get("unclaimed_cells") or []
    for p in uc:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))
        except:
            pass

    opp_t = set()
    ot = observation.get("opponent_territory") or []
    for p in ot:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))
        except:
            pass

    def adj_opp(nx, ny):
        if not opp_t:
            return 0
        for dx, dy in dirs:
            if (nx + dx, ny + dy) in opp_t:
                return 1
        return 0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 100000
        score += 3 * adj_opp(nx, ny)
        score -= abs(nx - ox) + abs(ny - oy)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    return [0, 0]