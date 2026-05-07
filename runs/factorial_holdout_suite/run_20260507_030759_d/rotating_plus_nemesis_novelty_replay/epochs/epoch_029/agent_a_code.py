def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer resources we can arrive at first (or tie), then maximize margin against opponent.
    best = None
    for rx, ry in resources:
        sd = cheb_dist(sx, sy, rx, ry)
        od = cheb_dist(ox, oy, rx, ry)
        arrive_first = 1 if sd <= od else 0
        margin = od - sd
        # Deterministic tie-breakers: favor closer, then lexicographic cell
        key = (arrive_first, margin, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    # Choose one-step move toward target; avoid obstacles; deterministically break ties.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb_dist(nx, ny, tx, ty)
        # Also slightly prefer moving away from opponent when margin is small
        d_opp = cheb_dist(nx, ny, ox, oy)
        score = (-d_to_t, d_opp, -dx, -dy, nx, ny)
        if best_m is None or score > best_m[0]:
            best_m = (score, dx, dy)
    return [best_m[1], best_m[2]]