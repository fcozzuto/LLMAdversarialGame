def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        if not ok(cx, cy):
            tx, ty = sx, sy
        else:
            tx, ty = cx, cy
    else:
        # Target resource that maximizes our advantage over opponent (deterministic).
        best_t = resources[0]
        best_score = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer closer, and when close, deny opponent by maximizing (do - ds).
            score = (do - ds) * 100 - ds
            if score > best_score or (score == best_score and (rx, ry) < best_t):
                best_score = score
                best_t = (rx, ry)
        tx, ty = best_t

    # If opponent is very close to our target, bias towards making progress in our own direction.
    dso = man(ox, oy, tx, ty)
    bias = -200 if dso <= 2 else 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds_n = man(nx, ny, tx, ty)
        ds_s = man(sx, sy, tx, ty)
        do_n = man(ox, oy, nx, ny)
        # Value: reduce distance to target; avoid giving opponent "nearby" opportunities; keep away from obstacles already handled.
        val = (ds_s - ds_n) * 50 - ds_n - (do_n * 2) + bias
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if ok(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]
    return [0, 0]