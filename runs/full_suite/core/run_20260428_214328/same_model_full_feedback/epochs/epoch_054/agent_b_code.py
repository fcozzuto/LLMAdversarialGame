def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inside(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target_score(tx, ty, nx, ny):
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        d_res_opp = man(ox, oy, tx, ty)
        # Prefer closer to resources than opponent; also stay away from opponent.
        return (d_self - d_res_opp) * 10 - d_opp

    if resources:
        # Deterministic: pick best move by evaluating all resources.
        t = int(observation.get("turn_index", 0))
        opp_bias = 1 if (t % 2 == 0) else 0
        best_move = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # Select the resource that most benefits us from this move.
            val = None
            for rx, ry in resources:
                v = best_target_score(rx, ry, nx, ny)
                if val is None or v > val:
                    val = v
            # Secondary tie-break: approach that move's closest resource; and maximize distance from opponent.
            # (Keeps behavior changing rather than oscillating.)
            closest = min((man(nx, ny, rx, ry) for rx, ry in resources), default=0)
            dist_opp = man(nx, ny, ox, oy)
            final_val = (val, -closest, dist_opp + opp_bias)
            if best_val is None or final_val > best_val:
                best_val = final_val
                best_move = [dx, dy]
        return best_move if best_move is not None else [0, 0]

    # No visible resources: drift to center while keeping away from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move, best_val = None, None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        score = -man(nx, ny, cx, cy) + man(nx, ny, ox, oy)
        if best_val is None or score > best_val:
            best_val = score
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]