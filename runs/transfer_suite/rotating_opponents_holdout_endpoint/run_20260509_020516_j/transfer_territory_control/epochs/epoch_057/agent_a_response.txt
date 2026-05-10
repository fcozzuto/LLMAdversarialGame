def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(v):
        s = set()
        for p in v or []:
            if p is None or len(p) < 2:
                continue
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1),(0,0)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def best_dist_from(a, s):
        if not s:
            return 10**9
        ax, ay = a
        dmin = 10**9
        for (x, y) in s:
            d = md(ax, ay, x, y)
            if d < dmin:
                dmin = d
        return dmin

    targets = resources if resources else (unclaimed if unclaimed else (unclaimed | opp_t))
    move_scores = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        gain = 0.0
        if (nx, ny) in opp_t:
            gain = 3.0
        elif (nx, ny) in unclaimed:
            gain = 1.7
        elif (nx, ny) in self_t:
            gain = 0.3
        else:
            gain = 0.2  # empty/unknown but reachable

        d_opp = md(nx, ny, ox, oy)
        d_tgt = best_dist_from((nx, ny), targets)

        # If we can steal immediate territory, prioritize; otherwise expand while keeping some distance from sweeper.
        away_bonus = 0.25 * d_opp if (not resources) else 0.05 * d_opp
        score = -(gain + away_bonus) * 1000 + d_tgt

        move_scores.append((score, -gain, -d_opp, dx, dy))

    if not move_scores:
        return [0, 0]
    move_scores.sort()
    return [int(move_scores[0][3]), int(move_scores[0][4])]