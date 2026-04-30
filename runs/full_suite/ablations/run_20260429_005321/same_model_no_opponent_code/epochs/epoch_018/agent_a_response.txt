def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_key = (-10**18, 10**18, 10**18)  # margin desc, self dist asc, tie by coordinates
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            # Prefer resources we can reach at least as fast; break ties by lower self distance then position
            key = (margin, -sd, -rx - ry)
            if margin > best_key[0] or (margin == best_key[0] and sd < best_key[1]):
                best = (rx, ry)
                best_key = (margin, sd, rx + ry)
            elif margin == best_key[0] and sd == best_key[1] and (rx + ry) < best_key[2]:
                best = (rx, ry)
                best_key = (margin, sd, rx + ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        opp_d_after = cheb(ox, oy, tx, ty)  # opponent won't move this turn; heuristic still fine
        dist_gain = cur_sd - nd  # positive if closer
        score = 1000 * dist_gain - 2 * nd + 0.1 * (cur_od - opp_d_after)
        # Deterministic tie-break: lexicographic by delta
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]