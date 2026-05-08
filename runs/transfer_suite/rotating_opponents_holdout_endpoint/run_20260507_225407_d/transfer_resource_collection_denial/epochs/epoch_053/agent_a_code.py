def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pre-rank resources by opponent advantage now (for stable top-k selection).
    now_opp = []
    for tx, ty in res:
        opp_d = man(ox, oy, tx, ty)
        now_opp.append((opp_d, (tx, ty)))
    now_opp.sort(key=lambda z: (z[0], z[1][0], z[1][1]))
    topk = [p for _, p in now_opp[:min(6, len(now_opp))]]

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Score by expected lead on best few resources if we keep heading there.
        s_best = 10**9
        score = 0
        for tx, ty in topk:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            lead = od - sd  # positive means we are closer
            s_best = min(s_best, sd)
            # Encourage immediate progress and beating opponent on likely targets.
            score += lead * 50 - sd * 3 + (-1 if (tx, ty) == (nx, ny) else 0) * 500

        # Additional pressure: if we are currently behind everywhere, move to reduce max distance gap.
        worst_gap = -10**9
        for tx, ty in topk:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            worst_gap = max(worst_gap, od - sd)
        score += worst_gap * 10

        # Prefer staying closer to current best resource to reduce oscillation.
        score -= s_best * 1

        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]