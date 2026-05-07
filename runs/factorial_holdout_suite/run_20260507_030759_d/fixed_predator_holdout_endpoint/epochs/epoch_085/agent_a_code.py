def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pre-rank resources by how good they are "in general" for us vs opponent (no move yet)
    ranked = []
    for r in res:
        myd = abs(r[0] - sx) + abs(r[1] - sy)
        opd = abs(r[0] - ox) + abs(r[1] - oy)
        # Prefer closer resources where we can arrive first
        ranked.append((opd - myd, -myd, r))
    ranked.sort(reverse=True)
    top = [t[2] for t in ranked[:6]] if len(ranked) > 6 else [t[2] for t in ranked]

    # Also include a quick focus on nearest resource to get deterministic "pull"
    nearest = min(res, key=lambda r: md((sx, sy), r))
    if nearest not in top:
        top = top[:-1] + [nearest] if len(top) >= 2 else [nearest]

    # Evaluate moves by projected advantage for top targets
    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res:
            return [dx, dy]  # deterministic immediate pickup

        my_pos = (nx, ny)
        val = 0
        # Encourage moves that make us arrive first (strongly), and secondarily that reduce our distance
        for r in top:
            myd = abs(r[0] - nx) + abs(r[1] - ny)
            opd = abs(r[0] - ox) + abs(r[1] - oy)  # opponent hasn't moved yet
            adv = opd - myd  # positive means we are closer (ignoring obstacles)
            # Boost if we gain/hold lead; otherwise still prefer reducing our own distance
            if adv > 0:
                val += 50 + 10 * adv
            else:
                val += -5 + adv
            val += -0.25 * myd

        # Denial against likely denier: avoid running directly into opponent's neighborhood while chasing
        # (prevents being "herded" by resource_denier behavior)
        dist_opp_now = abs(sx - ox) + abs(sy - oy)
        dist_opp_next = abs(nx - ox) + abs(ny - oy)
        if dist_opp_next <= dist_opp_now:
            val -= 2

        # Small tie-break: prefer reducing distance to the chosen nearest target
        val += -0.01 * md(my_pos, nearest)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]