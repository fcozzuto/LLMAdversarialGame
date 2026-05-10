def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = (manh(ox, oy, cx, cy), -manh(sx, sy, cx, cy))
            if bestv is None or v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((dx, dy, manh(nx, ny, tx, ty), manh(nx, ny, ox, oy)))
        candidates.sort(key=lambda t: (t[2], -t[3], t[0], t[1]))
        return [candidates[0][0], candidates[0][1]] if candidates else [0, 0]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_next_d = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        opp_d_nearest = min(manh(ox, oy, rx, ry) for rx, ry in resources)
        worst_resource_adv = -10**9
        sum_urgency = 0
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd
            if adv < worst_resource_adv:
                worst_resource_adv = adv
            urgency = 1.0 / (sd + 1)
            sum_urgency += urgency
        # Primary: how close we are to some resource; Secondary: advantage over opponent; Tertiary: avoid being "behind" on worst resource
        val = (-(self_next_d), worst_resource_adv, sum_urgency, -(opp_d_nearest), -manh(nx, ny, sx, sy))
        candidates.append((val, dx, dy))
    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3], t[0][4], t[1], t[2]), reverse=True)
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]