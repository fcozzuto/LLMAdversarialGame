def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Pick a primary target: minimize our lateness vs opponent on reachable-ish resources.
    best_t = None
    best_k = 10**18
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets where we are not far behind; strongly prefer any where we're ahead.
        k = (ds - do) * 1000 + ds
        if do <= 1 and ds > do:
            k += 20000
        if k < best_k:
            best_k = k
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Evaluate moves by their effect on (ds - do) and our absolute progress toward the target.
    best_move = (0, 0, sx, sy)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        rel_now = cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)
        rel2 = ds2 - do2
        # Reward reducing lateness; also reward decreasing distance.
        val = 0
        val += (rel_now - rel2) * 50
        val += (cheb(sx, sy, tx, ty) - ds2) * 10
        # Secondary consideration: avoid stepping into regions near obstacles.
        # (lightweight deterrent)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obst:
                    near += 1
        val -= near
        # Small bias to keep moving (if tied).
        if (dx, dy) != (0, 0):
            val += 0.1
        if val > best_val:
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]