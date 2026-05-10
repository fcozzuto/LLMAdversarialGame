def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    ti = int(observation.get("turn_index", 0) or 0)

    if not resources:
        tx = 0 if ((ti + ox + oy) & 1) == 0 else w - 1
        ty = 0 if ((ti + ox) & 1) == 0 else h - 1
        wantx = 1 if tx > sx else (-1 if tx < sx else 0)
        wanty = 1 if ty > sy else (-1 if ty < sy else 0)
        dx = wantx
        dy = wanty
        if dx == 0 and dy == 0:
            dx, dy = 0, 0
        return [int(dx), int(dy)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score: prefer resources we can reach no later than opponent, but with tie-breaking toward closer to opponent.
        local = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we arrive earlier: good. If later: bad. If same: prefer smaller ds.
            # Add a slight bias to avoid pass-by near resources behind: use ds.
            val = (do - ds, -ds, -(abs(rx - nx) + abs(ry - ny)))
            if local is None or val > local:
                local = val
        # Also include tiny obstacle-avoidance: fewer blocked neighbor directions.
        blocked = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if ax < 0 or ax >= w or ay < 0 or ay >= h or (ax, ay) in obstacles:
                blocked += 1
        key = (local[0], local[1], local[2], -blocked)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]