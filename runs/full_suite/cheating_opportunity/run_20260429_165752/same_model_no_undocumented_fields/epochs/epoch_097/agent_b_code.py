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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if resources:
        # Choose target: closest to us, tie-break by prefer resources closer to opponent (contest)
        best_t = None
        best_k = None
        for rx, ry in resources:
            k1 = cheb(sx, sy, rx, ry)
            k2 = cheb(ox, oy, rx, ry)
            if best_k is None or (k1, -k2, rx, ry) < best_k:
                best_k = (k1, -k2, rx, ry)
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    best_val = None
    # Fixed ordering tie-break for determinism
    for dx, dy, nx, ny in candidates:
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # If resources exist, slightly prefer reducing Manhattan as a tie-break
        d_to_t_man = man(nx, ny, tx, ty)
        # Prefer staying away from opponent while still chasing target
        val = (-d_to_t) * 10 + (d_to_opp) * 2 - d_to_t_man * 0.1
        # If stepping onto/adjacent to target (with no obstacles) is good; small boost
        if resources and (nx, ny) == (tx, ty):
            val += 1000
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]