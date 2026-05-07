def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Prefer we arrive first; then maximize lead; then closer; then prefer smaller coordinates deterministically.
        key = (sd <= od, od - sd, -sd, -(rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dxs = [0, 1, -1] if tx != sx else [0]
    dys = [0, 1, -1] if ty != sy else [0]

    best_move = [0, 0]
    best_move_key = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            nsd = md(nx, ny, tx, ty)
            nod = md(nx, ny, ox, oy)
            # Reduce distance to target, while keeping good race conditions against opponent.
            key = (-nsd, nod, -(abs(tx - (sx + dx)) + abs(ty - (sy + dy))), -nx, -ny)
            if best_move_key is None or key > best_move_key:
                best_move_key = key
                best_move = [dx, dy]

    return best_move