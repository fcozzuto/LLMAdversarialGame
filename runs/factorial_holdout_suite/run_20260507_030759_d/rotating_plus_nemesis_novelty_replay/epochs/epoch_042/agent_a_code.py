def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    # Deterministic tie-break: prefer smaller dx, then smaller dy in fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # If we land on a resource now, value it highly.
        score = 0
        landed = 0
        if resources:
            for (rx, ry) in resources:
                if rx == nx and ry == ny:
                    landed += 1
        if landed:
            score += 10**7 * landed

        # Otherwise, evaluate best competitive target advantage.
        if resources:
            my_best = 10**9
            opp_best = 10**9
            for (rx, ry) in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Advantage: positive means we're closer (or at least not worse)
                # Also encourage smaller absolute distances to finish before opponent.
                adv = od - md
                if md < my_best:
                    my_best = md
                if od < opp_best:
                    opp_best = od
                # Weight: prioritize targets where we are currently closer than opp
                score += (adv * 2000) - (md * 35)
                # For closer resources, add a mild bonus to speed collection
                if md == 0:
                    score += 5000
            # If we're generally farther, penalize to avoid wandering
            score -= (my_best * 6) + (opp_best * 1)

        # Obstacle avoidance already handled by legality; add slight pressure to not go out of bounds
        # Encourage moving toward the global center when no resources are visible.
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -cheb(nx, ny, cx, cy) - cheb(nx, ny, ox, oy) * 0.05

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]