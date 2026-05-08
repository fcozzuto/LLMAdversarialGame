def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d = abs(x - cx) + abs(y - cy)
        return -0.03 * d

    def terr_centroid(terrset, fallback):
        if not terrset:
            return fallback
        xs = [p[0] for p in terrset]
        ys = [p[1] for p in terrset]
        return int(round(sum(xs) / len(xs))), int(round(sum(ys) / len(ys)))

    pcx, pcy = terr_centroid(opp_terr, (ox, oy))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def reward(x, y):
        if (x, y) in opp_terr:
            r = 7.0
        elif (x, y) in unclaimed:
            r = 3.2
        elif (x, y) in self_terr:
            r = 0.7
        else:
            r = 0.2
        if (x, y) in resources:
            r += 2.1
        # Prefer approaching opponent-controlled center area.
        r += -0.08 * (abs(x - pcx) + abs(y - pcy))
        # Slightly prefer central expansion.
        r += center_bias(x, y)
        return r

    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        s1 = reward(nx, ny)
        # 1-step lookahead for more consistent territory capture.
        best2 = -10**9
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not legal(tx, ty):
                continue
            # Keep it deterministic and cheap: prioritize captures.
            sc = reward(tx, ty)
            if sc > best2:
                best2 = sc
        total = s1 + 0.65 * best2
        if total > best_score:
            best_score = total
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]