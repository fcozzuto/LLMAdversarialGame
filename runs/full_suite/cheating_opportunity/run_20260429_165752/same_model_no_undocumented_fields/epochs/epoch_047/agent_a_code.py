def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we have an advantage in (self distance - opp distance).
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (d_me - d_op, d_me, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no clear advantage (or no resources), fall back to center.
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        # Require some advantage; otherwise target closest resource to self anyway.
        if best_key[0] > 0:
            dmin = None
            for rx, ry in resources:
                dm = cheb(sx, sy, rx, ry)
                if dmin is None or dm < dmin[0] or (dm == dmin[0] and (rx, ry) < (dmin[1], dmin[2])):
                    dmin = (dm, rx, ry)
            tx, ty = dmin[1], dmin[2]
        else:
            tx, ty = best

    # Evaluate one-step moves: prefer reducing distance to target, and being farther from opponent.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_me = cheb(nx, ny, tx, ty)
        d_op_to_target = cheb(ox, oy, tx, ty)
        # Prefer moves that keep target chase while not walking into immediate opponent race.
        # Secondary: avoid moves that increase opponent's ability to reach some resource.
        v = (d_me, )  # minimize
        # Slight deterministic tie-breaker: prefer smaller lex move.
        if best_val is None or v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]