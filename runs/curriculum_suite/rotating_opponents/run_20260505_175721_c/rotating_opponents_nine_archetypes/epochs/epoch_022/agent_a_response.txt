def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if resources:
        # Choose resource to maximize (opponent_arrival - our_arrival), tie-break by earliest our time then coords.
        best = None
        for rx, ry in resources:
            st = cheb(sx, sy, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            adv = ot - st
            cand = (-adv, st, rx, ry)  # deterministic min
            if best is None or cand < best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic ordering prefers staying/straight less later; keep fixed order as above.
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: best if we reduce distance to target and also keep advantage vs opponent on that target.
        d0 = cheb(sx, sy, tx, ty)
        d1 = cheb(nx, ny, tx, ty)
        st1 = d1
        ot = cheb(ox, oy, tx, ty)
        adv1 = ot - st1
        # Prefer progress (d1 smaller), then larger advantage (adv1), then closer overall to target.
        score = (d1, -adv1, d0 - d1, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]