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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        scored = []
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            margin = d_op - d_me  # positive means we arrive earlier (in king metric)
            scored.append((-(margin >= 1), -(margin), d_me, tx, ty, margin))
        scored.sort()
        # Prefer a resource we can reach earlier; if none, contest the best opponent target.
        best = None
        for item in scored:
            if item[5] >= 1:
                best = item
                break
        if best is None:
            # contest: pick resource maximizing opponent advantage, i.e., smallest (d_me - d_op)
            best = min(scored, key=lambda t: (t[2] - t[5], t[2], t[3], t[4]))
        tx, ty = int(best[3]), int(best[4])
    else:
        tx, ty = (w // 2), (h // 2)

    best_move = (0, 0)
    best_key = None
    # Step towards target; break ties by distancing from opponent and avoiding dead-ends.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_op = cheb(nx, ny, ox, oy)
        # simple local "safety": count valid moves next (more options preferred)
        options = 0
        for ax, ay in moves:
            xx, yy = nx + ax, ny + ay
            if valid(xx, yy):
                options += 1
        key = (d_to_t, -d_from_op, -options, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]