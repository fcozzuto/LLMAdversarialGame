def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Target the closest resource if available, but avoid moving onto or adjacent to opponent's position
    target = None
    best_score = None
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # distance to resource after move
            for r in resources:
                d = dist_cheb((nx, ny), r)
                # reward: closer to resource, penalize proximity to opponent to avoid capture
                opp_dist = dist_cheb((nx, ny), opp_pos)
                score = -d
                if opp_dist <= 1:
                    score -= 5
                if best_score is None or score > best_score:
                    best_score = score
                    target = (dx, dy)
        if target is not None:
            return [target[0], target[1]]

    # Fallback: move to maximize distance from opponent, while staying in bounds and not on obstacle
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d2op = dist_cheb((nx, ny), opp_pos)
        score = d2op
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # If no move found (shouldn't happen), stay
    return [0, 0]