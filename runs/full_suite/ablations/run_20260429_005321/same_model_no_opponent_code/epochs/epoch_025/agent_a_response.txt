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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
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
        return dx if dx > dy else dy

    ordered_deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)

    best_t = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; otherwise deny by being nearer.
        val = (od - sd) * 4 - sd
        # Small deterministic tie-break to vary over time.
        val += ((rx * 3 + ry * 5 + ti) % 7) * 0.01
        if val > best_val or (val == best_val and cheb(sx, sy, rx, ry) < cheb(sx, sy, best_t[0], best_t[1])):
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = [0, 0]
    best_score = 10**18
    best_secondary = -10**18
    for dx, dy in ordered_deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        # Prefer improving our distance, and secondarily worsen opponent's distance to the same target.
        nosd = cheb(ox, oy, tx, ty)
        # Approx: if we move toward target, opponent likely stays; use nsd compared to nosd to break ties.
        score = nsd
        secondary = (nosd - nsd)
        if score < best_score or (score == best_score and secondary > best_secondary):
            best_score = score
            best_secondary = secondary
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]