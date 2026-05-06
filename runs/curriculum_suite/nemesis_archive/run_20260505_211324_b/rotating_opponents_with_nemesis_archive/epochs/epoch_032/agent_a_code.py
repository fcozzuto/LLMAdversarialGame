def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_best = min(res, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))
    opp_best_d = md(ox, oy, opp_best[0], opp_best[1])

    def cell_score(px, py):
        best = -10**9
        for tx, ty in res:
            myd = md(px, py, tx, ty)
            opd = md(ox, oy, tx, ty)
            base = (opd - myd) * 3 - myd
            contest = 0
            if (tx, ty) == opp_best:
                contest += 20
            else:
                # If opponent is relatively close, prioritize denial
                if opd <= opp_best_d + 1:
                    contest += 8
            # Prefer nearer resources for takeover when not directly denying
            seize = 0
            if myd <= 2:
                seize += 10
            s = base + contest + seize
            if s > best:
                best = s
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            val = cell_score(sx, sy) - 1  # discourage obstacle collisions deterministically
        else:
            val = cell_score(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]
    return best_move