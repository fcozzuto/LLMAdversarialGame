def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))

    if not cands:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If resources exist: move toward best resource but add a defensive term against opponent proximity.
    if resources:
        best = None
        best_val = -10**18
        prefer_block = (observation.get("turn_index", 0) % 3 == 0)
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            # Resource term: prefer smaller distance to the closest resource; if on resource, dominate.
            mind = 10**9
            closest = None
            for rx, ry in resources:
                d = max(0, man(nx, ny, rx, ry))
                if d < mind:
                    mind = d
                    closest = (rx, ry)
            res_val = 1000 - mind * 3
            if closest and (nx, ny) == closest:
                res_val += 500

            # Defensive/blocking term: if moving makes opponent closer to resources, penalize; else reward.
            opp_closest_dist = 10**9
            for rx, ry in resources:
                d = man(ox, oy, rx, ry)
                if d < opp_closest_dist:
                    opp_closest_dist = d
            # Our move should ideally increase opponent's distance to their closest resource, or reduce ours faster.
            opp_term = (opp_closest_dist - man(ox, oy, closest[0], closest[1])) if closest else 0
            # Since we can't control opponent directly, use a proxy: avoid positions that allow easy interception
            # by matching our move toward the same region as opponent.
            block_val = 0
            if closest:
                block_val = -man(nx, ny, closest[0], closest[1]) + man(ox, oy, closest[0], closest[1])
            val = res_val
            if prefer_block:
                val += -opp_term * 0.5 + block_val * 0.2
            else:
                val += block_val * 0.35
            # Tie-break deterministically by move order.
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: go to opponent's corner deterministically to reduce their control.
    target_x = w - 1 if sx < w - 1 else 0
    target_y = h - 1 if sy < h - 1 else 0
    best = cands[0]
    best_val = -10**18
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, target_x, target_y)
        val = -d
        if val > best_val or (val == best_val and (dx, dy) == best):
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]