def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    if not resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0) or 0)
    parity = (sx + sy + turns) & 1

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_value(rx, ry):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if ((rx + ry) & 1) != parity:
            adv -= 0.15
        # extra bias: prefer resources in/near opponent's likely sweep direction (row/column pressure)
        row_bias = -0.05 * abs(ry - oy)
        col_bias = -0.05 * abs(rx - ox)
        return (adv, -sd, -od, rx, ry)

    # choose best target by advantage
    best = None
    bestk = None
    for rx, ry in resources:
        k = cell_value(rx, ry)
        if best is None or k > bestk:
            best = (rx, ry)
            bestk = k
    rx, ry = best

    # choose move that reduces distance to target, while preventing stepping onto obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = man(nx, ny, rx, ry)
        nod = man(nx, ny, ox, oy)
        # If we can collect soon, strongly prefer it; otherwise, keep safe tempo vs opponent
        # (ties broken deterministically by move ordering through best comparison)
        s = (-nsd, nod, -abs(nx - rx), -abs(ny - ry), dx, dy)
        if best_s is None or s > best_s:
            best_s = s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]