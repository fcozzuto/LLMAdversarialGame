def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If only a couple resources remain, bias strongly toward closest we can get first.
    remain = observation.get("remaining_resource_count", len(res_set)) or len(res_set)
    urgency = 1.0 if remain <= 4 else 0.6

    best = None
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            return [dx, dy]

        # Race to resources
        v = 0.0
        for rx, ry in res_set:
            d_self = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            # Prefer resources where self arrives no later than opponent
            race = (d_opp - d_self)
            # Encourage getting nearer (small distance)
            closeness = -0.15 * d_self
            # Encourage attacking the densest nearby cluster deterministically
            v += urgency * (1.8 * race + closeness)

        # Avoid stepping into immediate opponent takeover region
        # (penalize moves that reduce opponent advantage too much)
        opp_press = manh(nx, ny, ox, oy)
        v -= 0.08 * (7 - opp_press) if opp_press < 7 else 0.0

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    # Deterministic tie-break: fixed order
    if best is None:
        return [0, 0]
    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestdxdy = best
    for cand in order:
        if cand in legal:
            # recompute equality by reselecting best if same value
            # (kept simple: if v equal, choose earliest in order)
            break
    return [bestdxdy[0], bestdxdy[1]]