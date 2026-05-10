def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obs = to_set(observation.get("obstacles"))
    un = to_set(observation.get("unclaimed_cells", observation.get("unclaimed")))
    res = to_set(observation.get("resources"))
    st = to_set(observation.get("self_territory"))
    ot = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obstacle(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (x + ax, y + ay) in obs:
                    return True
        return False

    def eval_cell(x, y):
        if (x, y) in obs:
            return -10**9
        score = 0
        if (x, y) in res:
            score += 40
        if (x, y) in un:
            score += 16
        if (x, y) in ot:
            score += 10  # flipping on entry
        if (x, y) in st:
            score += 2   # safe extension
        if adj_obstacle(x, y):
            score -= 8

        d_center = abs(x - cx) + abs(y - cy)
        d_opp = abs(x - ox) + abs(y - oy)
        score += int(20 - d_center)  # press toward center to contest
        score += int(min(12, d_opp)) // 2  # mildly prefer away from opponent to avoid wasting

        # prefer moves that reduce distance to center
        sx_c = abs(sx - cx) + abs(sy - cy)
        score += 6 if d_center < sx_c else 0
        return score

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inb(x, y):
            continue
        sc = eval_cell(x, y)
        tieb = (abs(x - cx) + abs(y - cy), abs(x - ox) + abs(y - oy), x, y)
        if sc > best[0] or (sc == best[0] and tieb < best[1:]):
            best = (sc, tieb[0], tieb[1], dx, dy)

    return [int(best[3]), int(best[4])]