def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a strategic target: when we can beat opponent, go for maximum lead;
    # otherwise, minimize our distance while staying safer vs opponent.
    best = None
    best_margin = None
    best_sd = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        if best is None or margin > best_margin or (margin == best_margin and sd < best_sd):
            best = (rx, ry)
            best_margin = margin
            best_sd = sd
    target = best

    # Evaluate candidate moves with obstacle handling and safety.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tX, tY = target
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Base: progress to target (chebyshev).
        dist_t = cheb(nx, ny, tX, tY)
        cur_dist_t = cheb(sx, sy, tX, tY)

        # Safety: keep distance from opponent; when we have no lead, prioritize safety more.
        dist_o = cheb(nx, ny, ox, oy)
        cur_dist_o = cheb(sx, sy, ox, oy)

        if best_margin >= 0:
            # We are ahead for the chosen target: maximize closing while not suicidally approaching.
            score = (cur_dist_t - dist_t) * 10 + (dist_o - cur_dist_o)
        else:
            # Opponent is closer overall: chase carefully and stay away.
            score = (-(dist_t)) * 3 + (dist_o) * 6 + (dist_o - cur_dist_o)

        # Tie-breakers deterministic: prefer staying if equal, else lexicographically smallest move.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) == (0, 0) and best_move != (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]