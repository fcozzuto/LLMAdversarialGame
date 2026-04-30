def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (0, 0))
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    if not resources:
        # drift toward center
        tx, ty = w // 2, h // 2
    else:
        def dist(a, b):
            ax, ay = a
            bx, by = b
            dx = ax - bx
            dy = ay - by
            return abs(dx) + abs(dy)
        best = None
        for rx, ry in resources:
            dself = dist((sx, sy), (rx, ry))
            dop = dist((ox, oy), (rx, ry))
            # prioritize resources we are relatively closer to (smaller dself-dop)
            key = (dself - dop, dself, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_mv = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        # Evaluate: move closer to target, keep some distance from opponent, avoid stepping onto opponent
        dtn = abs(nx - tx) + abs(ny - ty)
        d_op = abs(nx - ox) + abs(ny - oy)
        on_op_pen = 10 if (nx, ny) == (ox, oy) else 0
        # also slightly prefer moves that reduce distance from opponent to us (deny their chase)
        d_op_now = abs(sx - ox) + abs(sy - oy)
        deny = (d_op_now - d_op)
        val = (dtn, -d_op, deny, on_op_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_mv = [dx, dy]
    return [int(best_mv[0]), int(best_mv[1])]