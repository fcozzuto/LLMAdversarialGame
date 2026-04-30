def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti % 2:
        moves = moves[1:] + moves[:1]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_target = None
    best_gain = -10**18
    # Choose a resource where we have a distance advantage over the opponent.
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        center_bias = (abs(x - cx) + abs(y - cy)) * 0.001
        gain = (do - ds) - center_bias
        # Deterministic tie-break: prefer lower ds, then x,y
        if gain > best_gain + 1e-9 or (abs(gain - best_gain) <= 1e-9 and (best_target is None or (ds, x, y) < (cheb(sx, sy, best_target[0], best_target[1]), best_target[0], best_target[1]))):
            best_gain = gain
            best_target = (x, y)

    # If no resources, drift toward center while avoiding obstacles.
    if not best_target:
        tx, ty = int(round(cx)), int(round(cy))
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Local evaluation: maximize next-step advantage against the chosen target.
        myd = cheb(nx, ny, tx, ty)
        odd = cheb(ox, oy, tx, ty)
        # If we can reach it sooner than opponent, strongly prefer it.
        reach_bonus = (odd - myd) * 10.0
        # Mild pressure to keep moving toward target.
        step_bonus = -(myd)
        # Obstacle proximity penalty: discourage moves that are adjacent to many obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    adj += 1
        score = reach_bonus + step_bonus - adj * 0.2
        if score > best_score + 1e-9 or (abs(score - best_score) <= 1e-9 and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]