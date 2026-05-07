def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def cell_value(cx, cy, tx, ty):
        sd = dist((cx, cy), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        # Prefer resources we can arrive no later than opponent; then maximize advantage.
        return (-(sd - od), -sd, tx, ty)

    # Pick target with maximal advantage for us (diagonal-metric).
    best_t = None
    best_k = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Strongly prefer tiles we can "steal" (sd <= od).
        k = (-(max(0, sd - od) + (sd > od) * 2), -(sd), (od - sd), rx, ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    # Choose one-step move that improves our one-step arrival to the same best target.
    best_move = [0, 0]
    best_mk = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            mk = cell_value(nx, ny, tx, ty)
            # Break ties by staying within bounds and reducing distance to opponent as a minor deterrent.
            mk = (mk, -dist((nx, ny), (ox, oy)))
            if best_mk is None or mk > best_mk:
                best_mk = mk
                best_move = [dx, dy]

    return best_move