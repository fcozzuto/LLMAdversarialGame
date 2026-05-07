def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        better_cnt = 0
        tie_cnt = 0
        best_margin = -10**9
        min_my = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if myd < opd:
                better_cnt += 1
                margin = opd - myd
                if margin > best_margin:
                    best_margin = margin
            elif myd == opd:
                tie_cnt += 1
            if myd < min_my:
                min_my = myd

        # Prefer: win at least one resource, maximize margin, break ties by fewer ties, then closer best resource.
        key = (better_cnt > 0, better_cnt, best_margin, -tie_cnt, -min_my, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]