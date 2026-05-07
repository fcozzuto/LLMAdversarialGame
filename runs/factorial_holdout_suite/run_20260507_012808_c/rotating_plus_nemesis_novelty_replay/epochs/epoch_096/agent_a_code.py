def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_toward(tx, ty):
        ddx = 0 if tx == sx else (1 if tx > sx else -1)
        ddy = 0 if ty == sy else (1 if ty > sy else -1)

        candidates = []
        candidates.append((ddx, ddy))
        candidates.append((ddx, 0))
        candidates.append((0, ddy))
        candidates.append((-ddx, 0))
        candidates.append((0, -ddy))
        candidates.append((0, 0))

        best = (0, 0)
        best_score = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # prefer reducing distance to target, and slightly avoid opponent
            d_my = manh(nx, ny, tx, ty)
            d_op = manh(nx, ny, ox, oy)
            score = -d_my * 100 - d_op
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    if not resources:
        tx, ty = w // 2, h // 2
        return step_toward(tx, ty)

    best_val = -10**30
    best_tx, best_ty = resources[0]
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # maximize advantage; also favor nearer targets when advantages tie
        val = (opd - myd) * 1000 - myd * 3 + (0 if (rx + ry) % 2 == 0 else 0.1)
        if val > best_val:
            best_val = val
            best_tx, best_ty = rx, ry

    return step_toward(best_tx, best_ty)