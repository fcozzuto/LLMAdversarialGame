def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer or equal
        # Secondary nudges: prefer targets roughly in our direction and not behind opponent
        toward = (rx - sx) * (rx - ox) + (ry - sy) * (ry - oy)
        key = (lead, toward, -(sd + 2 * od), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    # Deterministic tie-breaking order already encoded by list order.
    best_m = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        nd_self = cheb(nx, ny, rx, ry)
        nd_opp = cheb(ox, oy, rx, ry)
        lead_after = nd_opp - nd_self
        # If tied/behind for the chosen target, slightly prefer moves that also increase our lead
        # and decrease distance to alternative resources.
        alt_penalty = 0
        for arx, ary in resources:
            if (arx, ary) == (rx, ry):
                continue
            ad = cheb(nx, ny, arx, ary)
            ao = cheb(ox, oy, arx, ary)
            alt_penalty += 1 if (ao - ad) > 0 else 0

        mkey = (lead_after, -nd_self, alt_penalty, -abs((nx - rx)) - abs((ny - ry)), -dx, -dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]