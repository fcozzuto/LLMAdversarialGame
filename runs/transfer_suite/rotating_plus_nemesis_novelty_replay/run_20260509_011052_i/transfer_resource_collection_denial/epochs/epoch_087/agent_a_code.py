def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Counter sweep behavior: penalize resources aligned with opponent row/col unless we are strictly closer.
        aligned = (ry == oy) or (rx == ox)
        align_pen = 6 if aligned and od <= sd else (2 if aligned else 0)
        # Prefer not crossing past opponent: reward targets that keep us "ahead" in distance advantage.
        adv = od - sd
        key = (adv - align_pen, -sd, -od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    # Choose best next step toward target while avoiding stepping into obstacles when possible.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in obstacles:
                    candidates.append((1, cheb(nx, ny, tx, ty), dx, dy))
                else:
                    candidates.append((0, cheb(nx, ny, tx, ty), dx, dy))
    candidates.sort(key=lambda t: (t[0], t[1], -abs(ox - (sx + t[2])), -abs(oy - (sy + t[3])), t[2], t[3]))
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]