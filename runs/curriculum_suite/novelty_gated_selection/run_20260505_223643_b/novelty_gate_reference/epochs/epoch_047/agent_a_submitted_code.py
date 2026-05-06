def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(a, b, c, d):
        if a < c: a = c - a
        else: a = a - c
        if b < d: b = d - b
        else: b = b - d
        return a + b

    def center(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx, dy = x - cx, y - cy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_sc = -10**18
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tie = 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        sc = 0
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if d < dmin: dmin = d
            sc += 200 - 20 * dmin
            for rx, ry in resources:
                if manh(nx, ny, rx, ry) == 0:
                    sc += 400
                    break
        else:
            sc += 80 - 10 * center(nx, ny)

        dopp = manh(nx, ny, ox, oy)
        sc += 5 - dmin if resources else 0
        sc += 15 if dmanh(nx, ny, ox, oy) <= 2 else 0  # deterring by proximity to contest

        # Prefer not moving into immediate obstacle wall
        near_obs = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if (tx, ty) in obstacles:
                near_obs += 1
        sc -= 3 * near_obs

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
            tie = 0
        elif sc == best_sc and best is not None:
            tie += 1
            if tie % 2 == 0:
                best = [dx, dy]
    return best if best is not None else [0, 0]