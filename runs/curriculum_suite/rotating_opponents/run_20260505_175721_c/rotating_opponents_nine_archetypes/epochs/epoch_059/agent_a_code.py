def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)
    else:
        def md(a, b, c, d):
            dx = a - c
            if dx < 0: dx = -dx
            dy = b - d
            if dy < 0: dy = -dy
            return dx + dy

        best = None
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; break ties toward higher "tempo" (shorter our distance).
            # Also add slight center preference to avoid late-game stalemates.
            ccx, ccy = (w - 1) // 2, (h - 1) // 2
            center_boost = -(md(rx, ry, ccx, ccy))
            val = (od - sd, -sd, center_boost, rx, ry)
            if best is None or val > best[0]:
                best = (val, (rx, ry))
        target = best[1]

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = abs(nx - tx) + abs(ny - ty)
        od = abs(nx - ox) + abs(ny - oy)
        # Reduce distance to target; also keep away from opponent a bit (corner_guard punishes contact).
        center_tight = -(abs(nx - cx) + abs(ny - cy))
        val = (-sd, od, center_tight, dx, dy)
        if bestm is None or val > bestm[0]:
            bestm = (val, [dx, dy])

    if bestm is None:
        return [0, 0]
    return bestm[1]