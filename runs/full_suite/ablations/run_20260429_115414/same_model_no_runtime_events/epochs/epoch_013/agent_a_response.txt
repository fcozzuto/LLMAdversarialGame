def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # If no resources, drift toward center while respecting obstacles and opponent pressure.
    center = (w // 2, h // 2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        if res:
            # Evaluate best resource target under this move.
            # Encourage: becoming closer than opponent, and landing on/near a resource.
            # Also discourage: letting opponent be much closer to the same resource.
            local_best = -10**18
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # If we can reach this resource sooner (or tie), strongly prefer it.
                # If opponent is closer, it becomes a liability; smaller myd helps only slightly.
                advantage = opd - myd
                # Extra reward for landing on the resource immediately.
                land = 4 if (nx, ny) == (rx, ry) else 0
                # Small tie-breakers for determinism/steadiness.
                near_pen = 0.05 * myd
                opp_dist_bonus = 0.02 * (opd if advantage < 0 else opd * 0.5)
                score = 10 * advantage + land - near_pen + opp_dist_bonus
                # Prefer resources closer to the board center to avoid corner traps.
                score -= 0.01 * cheb(rx, ry, center[0], center[1])
                if score > local_best:
                    local_best = score
            # Mild global penalty if we are drifting away from resources in general.
            # Use current nearest resource distance as a deterministic check.
            my_near = min(cheb(nx, ny, r[0], r[1]) for r in res)
            local_best -= 0.1 * my_near
            score_total = local_best
        else:
            # No visible resources: move toward center, but avoid approaching opponent too directly.
            score_total = -0.7 * cheb(nx, ny, center[0], center[1]) + 0.15 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break by dir order (earlier in dirs wins).
        if score_total > best_score:
            best_score = score_total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]