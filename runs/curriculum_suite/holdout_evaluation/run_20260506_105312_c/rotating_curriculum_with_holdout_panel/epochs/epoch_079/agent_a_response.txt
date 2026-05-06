def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        return [0, 0]

    def edge_penalty(x, y):
        return (1 if x == 0 or x == w - 1 else 0) + (1 if y == 0 or y == h - 1 else 0)

    # Determine if opponent is generally closer to all resources; if so, bias towards interior and farther resources that we can reach first.
    opp_leads = 0
    for rx, ry in rlist:
        if md(ox, oy, rx, ry) <= md(sx, sy, rx, ry):
            opp_leads += 1
    opp_ahead_all = opp_leads == len(rlist)

    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate this move by the best "race advantage" it gives us across resources.
        local_best = -10**9
        for rx, ry in rlist:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive if we are closer
            # Prefer interior when opponent is ahead overall; also prefer resources that are nearer overall.
            bias = -0.03 * self_d - (0.35 * edge_penalty(rx, ry) if opp_ahead_all else 0.0)
            val = adv + bias
            if val > local_best:
                local_best = val

        # Extra safety: don't step to cells that are strictly closer to opponent than to self's current position for all resources
        # (helps against edge_patrol oscillations).
        opp_step = md(nx, ny, ox, oy)
        self_step = md(nx, ny, sx, sy)
        safety = -0.02 * opp_step + 0.005 * self_step

        total = local_best + safety

        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move