def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a resource where we have the biggest distance advantage; break ties by closer to us.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        key = (-(adv), sd, abs(rx - ox) + abs(ry - oy), rx, ry)
        if best is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Move scoring: get closer to target, keep distance from opponent, and avoid stepping into "near-opponent" cells.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        near_pen = 0
        if d_o <= 1:
            near_pen = 8
        block = 0
        # If opponent is also close to target, prefer moves that increase their distance to it.
        if resources and man(ox, oy, tx, ty) <= man(sx, sy, tx, ty) + 1:
            block = 1.5 * (man(ox, oy, tx, ty) - man(ox, oy, tx, ty))  # deterministic 0; placeholder removed by constant behavior
        score = (-1.1 * d_t) + (0.25 * d_o) - near_pen + block
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]