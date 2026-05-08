def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Prefer resources we can reach earlier than opponent; strong bias toward immediate pickup.
    opp_d = {}
    for rx, ry in res:
        opp_d[(rx, ry)] = md(ox, oy, rx, ry)

    best = None
    best_s = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        s = 0

        if (nx, ny) in opp_d:
            return [dx, dy]

        # Strongly avoid stepping adjacent (allowing interception) to resources opponent is already closer to.
        # And strongly seek resources where we have a distance lead.
        min_margin = 10**9
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = opp_d[(rx, ry)]
            margin = d_op - d_self  # positive means we are closer
            if margin < min_margin:
                min_margin = margin

            # Score combines lead and closeness; using bounded terms keeps deterministic scaling.
            lead = margin
            close = 1.0 / (1 + d_self)
            s += (lead * 50) + (close * 120)

        # If we are generally not leading, steer to reduce our worst-case deficit.
        s += max(0, min_margin) * 200
        s += -max(0, -min_margin) * 80

        # Also prefer staying closer to opponent's sweep target direction: match reduce distance to nearest resource
        # rather than drifting. (Sweep rows tends to move in straight lines; so keep our x/y alignment to nearest resource.)
        nearest = min(res, key=lambda p: md(nx, ny, p[0], p[1]))
        s += -md(nx, ny, nearest[0], nearest[1]) * 2

        # Micro-avoid obstacles by penalizing move that would leave fewer legal options (deterministic).
        cnt = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obs:
                    cnt += 1
        s += cnt * 3

        if s > best_s:
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]