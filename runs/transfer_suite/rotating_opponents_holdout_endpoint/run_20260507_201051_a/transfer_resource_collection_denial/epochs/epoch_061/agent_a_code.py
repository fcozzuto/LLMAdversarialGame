def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Identify opponent's closest resource to anticipate contests
    opp_target = min(resources, key=lambda r: (cheb(r[0], r[1], ox, oy), cheb(r[0], r[1], sx, sy), r[0], r[1]))

    # Choose our best resource: prefer ones we can beat the opponent to (or at least not lose badly)
    best = None
    for rx, ry in resources:
        my_t = cheb(rx, ry, sx, sy)
        op_t = cheb(rx, ry, ox, oy)
        beat = op_t - my_t  # positive means we are faster
        # Penalize heavily if opponent is much faster on their likely target
        focus_pen = 0
        if (rx, ry) == opp_target and my_t > op_t:
            focus_pen = 100 + (my_t - op_t) * 2
        # Lexicographic: maximize beat, then prefer smaller my_t, then deterministic coord
        key = (beat - focus_pen, -my_t, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Step towards target, avoiding obstacles if the direct move is blocked
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dist = cheb(nx, ny, tx, ty)
            # Prefer direct progress to reduce distance; deterministic tie-break
            candidates.append((dist, abs(nx - tx) + abs(ny - ty), dx, dy))
    if not candidates:
        return [0, 0]
    _, _, dx, dy = min(candidates, key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(dx), int(dy)]