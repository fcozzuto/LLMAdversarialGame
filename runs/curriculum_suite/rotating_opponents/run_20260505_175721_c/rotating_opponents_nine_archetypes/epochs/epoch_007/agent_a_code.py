def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = w // 2, h // 2
        best, bestv = [0, 0], 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles: 
                    continue
                v = dist(nx, ny, tx, ty)
                if v < bestv:
                    bestv, best = v, [dx, dy]
        return best

    # Precompute obstacle proximity penalty
    obs_nei = set()
    for ex, ey in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = ex + dx, ey + dy
                if inb(xx, yy) and (xx, yy) not in obstacles:
                    obs_nei.add((xx, yy))

    best_move, best_val = [0, 0], -10**18
    target_hint = None
    # Deterministically choose a "priority" resource to steer toward / contest
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        adv = (dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry))
        # Tie-breaker: closer to center
        cen = abs(rx - w // 2) + abs(ry - h // 2)
        key = (adv, -cen)
        if target_hint is None or key > target_hint[0]:
            target_hint = (key, (rx, ry))
    _, (prx, pry) = target_hint

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            step_pen = -5 if (nx, ny) in obs_nei else 0
            # Evaluate best action based on either capturing or contesting
            val = step_pen
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # If we're closer, reward strongly; if not, reduce opponent's edge by moving toward the resource.
                adv = opd - myd
                base = 30 * (1 if adv > 0 else -1)
                # Strong prefer: pick the nearest resource among those we can beat
                if adv > 0:
                    val += base + (50 - myd) - 2 * min(dist(nx, ny, prx, pry), 8)
                else:
                    # Contest: approach resource while keeping option to swing to prio
                    val += (-10) + (25 - myd) + (opd - myd)
                    # If opponent is extremely closer, slightly penalize
                    if opd + 1 <= myd:
                        val -= 12
            # Mild preference for not drifting away from priority
            val += -2 * dist(nx, ny, prx, pry)
            if val > best_val:
                best_val, best_move = val, [dx, dy]

    return best_move