def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in set((int(x), int(y)) for x, y in resources):
        return [0, 0]

    # Pick target resource with best current advantage (opponent farther than us)
    best_r = None
    best_key = (-10**9, -10**9, -10**9)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx - ry)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resource: move to reduce distance to nearest reachable resource ignoring advantage
        best_move = [0, 0]
        best_d = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = 10**9
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                if not inb(rx, ry) or (rx, ry) in obs:
                    continue
                dd = cheb(nx, ny, rx, ry)
                if dd < d: d = dd
            if d < best_d:
                best_d = d
                best_move = [dx, dy]
        return best_move

    tx, ty = best_r

    # Choose move that maximizes post-move advantage toward the target, with safety/tie-breaks
    best_move = [0, 0]
    best_val = (-10**9, -10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        advantage = od - sd
        # Prefer moves that keep us closer to the target and also reduce opponent's best chance locally
        dist_sum = sd + od
        key = (advantage, -sd, dist_sum)
        if key > best_val:
            best_val = key
            best_move = [dx, dy]
    return best_move