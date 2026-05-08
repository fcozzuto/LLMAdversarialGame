def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                try:
                    x, y = int(x), int(y)
                except:
                    continue
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**9, 0, 0)

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Prefer frontier capture; counter-claiming by entering opponent territory is strong.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        cell = (nx, ny)
        d_opp = dist(nx, ny, ox, oy)
        d_center = dist(nx, ny, (w - 1) // 2, (h - 1) // 2)

        # Immediate cell value
        if cell in resources:
            val = 8
        elif cell in opp_t:
            val = 7
        elif cell in unclaimed:
            val = 5
        elif cell in self_t:
            val = 3
        else:
            val = 1

        # Frontier pressure: how many useful neighbors the move would touch
        neigh = 0
        for ax, ay in dirs4:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                if (px, py) in unclaimed:
                    neigh += 2
                if (px, py) in opp_t:
                    neigh += 3
                if (px, py) in self_t:
                    neigh += 1

        # Avoid walking into opponent: if opponent is adjacent and cell is not beneficial, back off.
        opp_adj = abs(nx - ox) <= 1 and abs(ny - oy) <= 1
        risk = 0
        if opp_adj and cell not in opp_t and cell not in unclaimed:
            risk = 2

        score = val + neigh - 0.01 * d_opp - 0.001 * d_center - risk

        # Deterministic tie-break: larger score, then smaller |dx|+|dy|, then lexicographic dx,dy
        tiebreak = (abs(dx) + abs(dy), dx, dy)
        cand = (score, -tiebreak[0], -tiebreak[1] * 100 - tiebreak[2])
        if cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move