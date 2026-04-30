def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        bestd = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a few promising resources deterministically
    scored = []
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        t = (d, abs(rx - (w // 2)) + abs(ry - (h // 2)), rx, ry)
        scored.append((t, (rx, ry)))
    scored.sort(key=lambda x: x[0])
    top = [p for _, p in scored[:6]]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = 10**9
        for rx, ry in top:
            d = cheb(nx, ny, rx, ry)
            my_best = d if d < my_best else my_best

        opp_d = cheb(nx, ny, ox, oy)
        # Encourage closeness to our target; avoid letting opponent get too close.
        # Also slightly prefer moving in direction of our nearest resource to prevent dithering.
        if resources:
            nrx, nry = top[0]
            dir_bias = -cheb(nx, ny, nrx, nry)
        else:
            dir_bias = 0

        val = (my_best * 1000) - (opp_d * 5) + dir_bias

        cand = (val, dx, dy)
        if best_val is None or cand < (best_val, best_move[0], best_move[1]):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]