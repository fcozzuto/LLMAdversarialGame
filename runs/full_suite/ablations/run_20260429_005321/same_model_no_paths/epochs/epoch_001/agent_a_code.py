def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    # Pick a target resource to maximize advantage over opponent
    if resources:
        best = None
        best_adv = -10**18
        for r in resources:
            myd = d2((sx, sy), (r[0], r[1]))
            opd = d2((ox, oy), (r[0], r[1]))
            adv = opd - myd  # positive means I'm closer
            # tie-break deterministically: higher adv, then smaller my distance, then lexicographic
            key = (adv, -myd, -r[0], -r[1])
            if best is None or key > best_adv:
                best_adv = key
                best = r
        tx, ty = best[0], best[1]
    else:
        # No resources: drift toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose move that reduces distance to target; penalize obstacles and staying if possible
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            score = -10**18
        else:
            myd = d2((nx, ny), (tx, ty))
            # Encourage blocking: if I'm moving into a spot that makes opponent farther from target than me
            opd = d2((ox, oy), (tx, ty))
            block = opd - myd
            # Slight penalty for staying still
            stay_pen = 0 if (dx != 0 or dy != 0) else -5
            score = int(10_000_000 - myd * 100 + block * 50 + stay_pen)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]