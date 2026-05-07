def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Deterministic retreat to reduce getting blocked; prefer staying in bounds.
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (dist(nx, ny, ox, oy), -nx, -ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each candidate move by "contested advantage" over the closest resource cluster.
    # Prefer moves that secure a resource we can reach earlier than opponent; otherwise deny by minimizing opponent advantage.
    best = (0, 0)
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Small lookahead: only compare a few best candidates by immediate potential.
        scored = []
        for rx, ry in resources:
            d_self = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            # advantage > 0 means we are closer; strongly prefer immediate secure (d_self <= d_opp).
            adv = (d_opp - d_self)
            # tie-break: prefer nearer resources overall and stable movement (avoid drifting far away).
            v = (adv, -(d_self), -(abs(rx - sx) + abs(ry - sy)), -(rx + ry))
            scored.append(v)
        scored.sort(reverse=True)
        # Use top few to remain robust and deterministic
        top = scored[:3]
        v0 = top[0][0]
        v1 = sum(t[0] for t in top)
        v2 = top[0][1]  # negative d_self, higher is better
        v = (v0, v1, v2, -abs(dx), -abs(dy), dx + dy)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]