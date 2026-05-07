def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx = 0
    cy = 0
    for rx, ry in resources[:8]:
        cx += rx
        cy += ry
    cx //= min(8, len(resources))
    cy //= min(8, len(resources))

    best = (-10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs:
                continue

            # Evaluate move by best "relative arrival" to any resource
            best_adv = -10**18
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                adv = (do - ds) * 1000 - ds  # prioritize winning races, then faster
                if adv > best_adv:
                    best_adv = adv

            # Small preference for drifting toward resource mass
            centroid_bias = dist(nx, ny, cx, cy)
            val = best_adv - centroid_bias
            # Deterministic tie-break: smaller |dx|+|dy|, then dx, then dy
            tie = (abs(dx) + abs(dy), dx, dy)
            cand = (val, -tie[0], -tie[1], -tie[2])
            cur = (best[0], - (abs(best[1]) + abs(best[2])), -best[1], -best[2])
            if cand > cur:
                best = (val, dx, dy)

    return [int(best[1]), int(best[2])]