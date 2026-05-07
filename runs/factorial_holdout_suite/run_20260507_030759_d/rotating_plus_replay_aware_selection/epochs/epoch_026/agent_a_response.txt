def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_score = -10**18
    best_secondary = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # score over all resources: how much closer we are than opponent (positive is good)
        best_lead = -10**18
        best_self_dist = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            lead = do - ds
            if lead > best_lead:
                best_lead = lead
            if ds < best_self_dist:
                best_self_dist = ds

        # Extra deterministic tie-break: prefer being adjacent/at a resource, then prefer larger lead, then fewer steps to closest
        # (adjacent/at gives big boost)
        close_bonus = 0
        if best_self_dist == 0:
            close_bonus = 10**6
        elif best_self_dist == 1:
            close_bonus = 10**5
        elif best_self_dist == 2:
            close_bonus = 10**4

        score = close_bonus + best_lead
        secondary = -best_self_dist

        if score > best_score or (score == best_score and secondary > best_secondary):
            best_score = score
            best_secondary = secondary
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]