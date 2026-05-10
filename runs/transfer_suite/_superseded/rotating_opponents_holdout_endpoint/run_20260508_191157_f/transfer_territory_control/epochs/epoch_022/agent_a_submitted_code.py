def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (w - 1, h - 1))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((p[0], p[1]))
        except Exception:
            pass

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_terr.add((p[0], p[1]))
        except Exception:
            pass

    self_terr = set()
    for p in observation.get("self_territory") or []:
        try:
            self_terr.add((p[0], p[1]))
        except Exception:
            pass

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not inside(sx, sy):
        return [0, 0]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if unclaimed:
        targets = []
        for t in unclaimed:
            if t in opp_terr:
                continue
            if t in self_terr:
                continue
            targets.append(t)
        if not targets:
            targets = corners
    else:
        res = []
        for p in observation.get("resources") or []:
            try:
                res.append((p[0], p[1]))
            except Exception:
                pass
        targets = res[:20] if res else corners

    best_t = None
    best_score = 10**9
    for tx, ty in targets:
        s = manh(sx, sy, tx, ty)
        s += 2 * (tx, ty) == (px, py)
        if (tx, ty) in opp_terr:
            s += 1000
        if s < best_score:
            best_score = s
            best_t = (tx, ty)

    tx, ty = best_t if best_t else (px, py)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best_m = [0, 0]
    best_m_score = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        s = manh(nx, ny, tx, ty)
        if (nx, ny) in opp_terr:
            s += 5
        if (nx, ny) in self_terr:
            s -= 1
        if s < best_m_score:
            best_m_score = s
            best_m = [dx, dy]

    return best_m