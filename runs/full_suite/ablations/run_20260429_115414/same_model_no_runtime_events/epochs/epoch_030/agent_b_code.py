def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    # Precompute distances from opponent to each resource
    opp_ds = {}
    for tx, ty in resources:
        opp_ds[(tx, ty)] = cheb(ox, oy, tx, ty)

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            # Immediate pickup preference
            score = 10**12
        else:
            # Prefer reducing our distance to the best available resource, while denying opponent.
            my_best = 10**9
            deny_best = -10**9
            for tx, ty in resources:
                if (tx, ty) in obstacles:
                    continue
                d_me = cheb(nx, ny, tx, ty)
                d_op = opp_ds[(tx, ty)]
                if d_me < my_best:
                    my_best = d_me
                # deny when opponent is farther than we are
                deny_best = max(deny_best, (d_op - d_me))
            # Weight: strongly prefer being closer; then maximize relative advantage
            score = (-my_best) * 10 + deny_best * 3
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]