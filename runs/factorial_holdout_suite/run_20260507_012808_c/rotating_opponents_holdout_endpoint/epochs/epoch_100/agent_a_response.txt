def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return int(v[0]), int(v[1])
        except:
            return 0, 0

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = xy(p)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = xy(r)
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

    # Target selection: prioritize being closer than opponent (small myd-opd), then absolute distance, then bias away from center late.
    turn = int(observation.get("turn_index") or 0)
    late = 1 if int(observation.get("turns_remaining") or 0) < (w * h) // 3 else 0
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    best_tx, best_ty = resources[0]
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        margin = myd - opd  # negative => we are ahead
        dist_key = (myd, opd)
        center_dist = abs(tx - center_x) + abs(ty - center_y)
        # In late game, slightly prefer edges/corners for safer pathing against deniers.
        edge_bias = -center_dist if late else 0.0
        key = (margin, dist_key[0], dist_key[1], edge_bias)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    # Greedy one-step toward target with obstacle avoidance.
    dxs = -1, 0, 1
    dys = -1, 0, 1
    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # Tie-break: prefer cheb distance decrease, then alignment with target direction, then stay only if forced.
                curd = cheb(sx, sy, best_tx, best_ty)
                newd = cheb(nx, ny, best_tx, best_ty)
                delta = curd - newd
                align = -abs((best_tx - sx) - dx) - abs((best_ty - sy) - dy)
                stay_pen = 0 if (dx != 0 or dy != 0) else 0.5
                # If opponent is close to the same target, add a small urgency to decrease distance quickly.
                urg = cheb(ox, oy, best_tx, best_ty)
                key = (-delta, stay_pen, -align, urg, nx, ny)
                candidates.append((key, [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]