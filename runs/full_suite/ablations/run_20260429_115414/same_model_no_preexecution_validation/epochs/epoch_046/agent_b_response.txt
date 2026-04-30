def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # If no resources, drift toward center-biased corner to reduce being trapped by obstacles.
    if not resources:
        tx = (w - 1) // 2 + (0 if (observation.get("turn_index", 0) % 2) else 1)
        ty = (h - 1) // 2
        best = (0, 0)
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: prefer resources where we are not too far behind opponent; if behind, "deny" by taking nearer contested lanes.
    # Deterministic tie-breaking uses turn_index parity to alternate preference among equal candidates.
    t = int(observation.get("turn_index", 0) or 0)
    prefer_opponent_ahead = (t % 2 == 0)

    best_target = None
    best_score = 10**18
    for x, y in resources:
        d_me = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)

        # advantage term: negative is good (we want ourselves to arrive earlier).
        adv = d_me - d_op

        # incorporate proximity to us (small d_me) while discouraging risky late arrivals
        # also slightly penalize symmetric choices by adding a tiny deterministic offset based on coordinates
        coord_bias = ((x * 17 + y * 31) % 7) * 0.01
        score = 2.0 * adv + 0.35 * d_me + coord_bias

        # If opponent is clearly ahead, optionally choose a "deny" target (push score to focus on closer contested resources)
        if prefer_opponent_ahead and d_op + 0 < d_me:
            score -= 0.6  # make contested targets more attractive when we're behind

        if score < best_score:
            best_score = score
            best_target = (x, y)
        elif score == best_score and best_target is not None:
            # deterministic secondary tie-break: closer to opponent means more contestability
            bx, by = best_target
            if cheb(ox, oy, x, y) < cheb(ox, oy, bx, by):
                best_target = (x, y)

    tx, ty = best_target

    # Choose move that minimizes distance to target while keeping a small preference to increase separation from opponent when possible.
    best_move = (0, 0)
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty