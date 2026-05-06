def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if not moves:
        return [0, 0]

    if resources:
        ordered = sorted(resources, key=lambda r: (king_dist(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        ordered = []

    # If only a few resources exist, prefer them; otherwise just go for center/denial.
    center = (w - 1) / 2.0, (h - 1) / 2.0

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Primary: maximize our advantage on any resource we might contest.
        val = 0.0
        if ordered:
            # Consider top-N closest resources to keep deterministic and fast.
            take = ordered[:min(6, len(ordered))]
            best_adv = -10**18
            closest_opp = 10**9
            for rx, ry in take:
                d_me = king_dist(nx, ny, rx, ry)
                d_op = king_dist(ox, oy, rx, ry)
                adv = (d_op - d_me)  # positive means we are closer than opponent
                # Reward proximity (both if we are close) while still valuing advantage.
                score = 4.0 * adv - 0.25 * d_me + 0.05 * (6 - d_op)
                if adv > best_adv:
                    best_adv = adv
                # Track worst-case: avoid moving into situations where opponent gets a resource very fast.
                closest_opp = min(closest_opp, d_op)
                val = max(val, score)
            # If we aren't clearly winning any contest, reduce moving into opponent-favored regions.
            if best_adv <= 0:
                val -= 0.6 * closest_opp
        else:
            # No resources: steer toward center but keep distance from opponent.
            cx, cy = center
            val = -king_dist(nx, ny, int(cx), int(cy)) - 0.2 * king_dist(nx, ny, ox, oy)

        # Secondary: avoid hard collisions with obstacles already handled by ok(); add mild opponent chase control.
        val -= 0.02 * king_dist(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            # Deterministic tie-breaker
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]