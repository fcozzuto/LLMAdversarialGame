def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    if w <= 0 or h <= 0:
        return [0, 0]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells") or []
    opp_pos = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0) % len(dirs)
    dirs = [dirs[(i + t) % len(dirs)] for i in range(len(dirs))]

    opp_terr = observation.get("opponent_territory") or []
    opp_terr = [(int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2]
    self_terr = observation.get("self_territory") or []
    self_terr = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2)

    use_opp = False
    if opp_terr:
        d0 = (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy)
        use_opp = d0 <= 25

    tx, ty = ox, oy
    if use_opp and opp_terr:
        bestd = 10**18
        for x, y in opp_terr:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if d < bestd:
                bestd = d
                tx, ty = x, y
    else:
        if unclaimed:
            bestd = 10**18
            best = None
            for p in unclaimed:
                if not isinstance(p, (list, tuple)) or len(p) < 2:
                    continue
                x, y = int(p[0]), int(p[1])
                if (x, y) in obs:
                    continue
                d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                if d < bestd:
                    bestd = d
                    best = (x, y)
            if best is not None:
                tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        score = d
        if (nx, ny) in self_terr:
            score -= 3
        if (nx, ny) == (ox, oy):
            score -= 50
        if score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move