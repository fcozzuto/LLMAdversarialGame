def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    occ_res = set(resources)

    best_move = (0, 0)
    best_score = -10**9

    # Two-phase target: (1) immediate grab if possible, else (2) move to swing advantage over opponent
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic: prefer immediate resource, then maximize (opp_dist - self_dist) to resources
        score = 0
        if (nx, ny) in occ_res:
            score += 10000

        # Encourage approaching resources where we become relatively closer than opponent
        for rx, ry in resources:
            ds_now = cheb(sx, sy, rx, ry)
            do_now = cheb(ox, oy, rx, ry)
            ds_n = cheb(nx, ny, rx, ry)
            do_n = cheb(ox, oy, rx, ry)  # opponent doesn't move this turn in our heuristic

            # If we can flip who is closer, that's valuable; if we are behind, reduce it.
            flip = (do_now - ds_now) - (do_n - ds_n)
            advantage = (do_n - ds_n)

            # Also add slight preference for shorter distance (stable).
            dist_pref = -ds_n

            # Obstacle-aware bias: avoid moves that would put us on/near a wall-heavy corner by discouraging extremes
            wall_bias = 0
            if nx == 0 or nx == w - 1: wall_bias -= 1
            if ny == 0 or ny == h - 1: wall_bias -= 1

            score += (2500 * (1 if advantage > 0 else -1)) if advantage != 0 else 0
            score += 120 * flip
            score += 8 * dist_pref
            score += wall_bias

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Deterministic tie-breaker
    if best_score == -10**9:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]