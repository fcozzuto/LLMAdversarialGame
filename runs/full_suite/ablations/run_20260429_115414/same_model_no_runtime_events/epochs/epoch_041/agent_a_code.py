def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick best target by current "gain"
    best_r = resources[0]
    best_gain = -10**18
    for r in resources:
        gain = cheb((ox, oy), r) - cheb((sx, sy), r)
        # prefer nearer for us on ties
        if gain > best_gain or (gain == best_gain and cheb((sx, sy), r) < cheb((sx, oy), r)):
            best_gain = gain
            best_r = r

    # evaluate moves; deterministic tie-breaking by direction order
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = best_r
    late = int(observation.get("remaining_resource_count", len(resources)) or len(resources)) <= 4

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        d_me = cheb((nx, ny), t)
        d_op = cheb((ox, oy), t)
        # main: reduce our distance, maximize separation in speed to target
        score = (d_op - d_me) * 10

        # secondary: steer toward best_r (closer is better)
        score += (cheb((sx, sy), t) - d_me)

        # prevent standing into opponent capture zone: if we end closer to their position than them to us, penalize
        d_our_to_op = cheb((nx, ny), (ox, oy))
        d_op_to_us_next = cheb((ox, oy), (sx, sy))
        if d_our_to_op <= d_op_to_us_next and d_our_to_op <= 2:
            score -= 6

        # late game: prioritize any immediate reachable resource over target-only
        if late:
            alt_best = None
            alt_val = -10**18
            for r in resources:
                v = (cheb((ox, oy), r) - cheb((nx, ny), r)) * 10 - cheb((nx, ny), r)
                if v > alt_val:
                    alt_val = v
                    alt_best = r
            score = score * 0.6 + alt_val * 0.4

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]