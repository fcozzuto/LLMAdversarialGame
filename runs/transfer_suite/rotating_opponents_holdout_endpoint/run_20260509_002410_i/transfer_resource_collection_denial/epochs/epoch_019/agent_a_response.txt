def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacle_set:
                if (x, y) != (sx, sy):
                    resset.append((x, y))
    if not resset:
        return [0, 0]

    best = resset[0]
    best_key = None
    for rx, ry in resset:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # win race first, then closer, then deterministic cell tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    cur_d = dist(sx, sy, tx, ty)
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        nd = dist(nx, ny, tx, ty)
        # prefer getting closer, but also avoid giving opponent a better race
        my_adv = (dist(ox, oy, tx, ty) - nd)
        key = (-nd, -(nd - cur_d), my_adv, -dx, -dy)  # deterministic tie-break
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]