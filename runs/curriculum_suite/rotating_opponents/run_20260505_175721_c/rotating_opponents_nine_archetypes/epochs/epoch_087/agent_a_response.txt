def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    best = None  # (score, tx, ty)
    for tx, ty in resources:
        self_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # We prefer resources we can reach no later than opponent; otherwise we deny.
        if self_d <= opp_d:
            score = (opp_d - self_d + 1) * 100000 - self_d * 100 - (abs(tx - sx) + abs(ty - sy))
        else:
            score = (100000 - (self_d - opp_d) * 1000) - opp_d * 10 - (abs(tx - sx) + abs(ty - sy))
        if best is None or score > best[0] or (score == best[0] and cheb(sx, sy, tx, ty) < cheb(sx, sy, best[1], best[2])):
            best = (score, tx, ty)

    _, tx, ty = best

    # Choose a legal step that minimizes distance to target, with deterministic tie-breaking.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = None  # (dist, -progress, idx, dx, dy)
    for idx, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        progress = cheb(sx, sy, tx, ty) - dist
        cand = (dist, -progress, idx, dx, dy)
        if best_step is None or cand < best_step:
            best_step = cand

    if best_step is None:
        return [0, 0]
    return [int(best_step[3]), int(best_step[4])]