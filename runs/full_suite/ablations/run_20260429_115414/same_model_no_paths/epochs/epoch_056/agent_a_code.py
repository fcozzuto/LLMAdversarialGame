def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1, h - 1)
        if (sx + sy) % 2 == 0: tx, ty = (w - 1, 0)
        target = (tx, ty)
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; tie-break by position
            key = (ds - do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        on_res = (nx, ny) == (tx, ty) and any((nx, ny) == r for r in resources)
        d_us = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # If opponent is closer, prioritize blocking by getting there too; else just rush target
        rivalry = (d_us - d_opp)
        # Also subtly keep distance from obstacles by preferring safer squares (fewer adjacent obstacle hits)
        adj_obs = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if not valid(px, py):
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj_obs += 1
        val = 0
        val += 100000 if on_res else 0
        val -= 1000 * rivalry
        val -= 10 * d_us
        val -= 2 * adj_obs
        # deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]