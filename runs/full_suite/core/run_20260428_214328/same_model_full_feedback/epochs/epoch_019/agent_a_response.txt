def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def obst_adj(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # fallback: drift away from opponent while avoiding obstacle adjacency
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_op = cheb(nx, ny, ox, oy)
            val = -d_op + 0.25 * obst_adj(nx, ny)
            if val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best_move = (10**18, 0, 0)
    # pick best resource deterministically
    best_res = None
    best_res_val = -10**18
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer closer-to-us and farther-from-opponent; slight bias for being away from obstacles
        util = (do - du) - 0.06 * obst_adj(rx, ry)
        if util > best_res_val:
            best_res_val = util
            best_res = (rx, ry)

    rx, ry = best_res
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        du = cheb(nx, ny, rx, ry)
        # discourage moving into crowded obstacle-adjacent areas
        risk = 0.15 * obst_adj(nx, ny)
        # if opponent is also close to the target, we prioritize reducing our distance more
        do_next = cheb(ox, oy, rx, ry)
        # deterministic tie-breaker by smaller dx,dy lexicographic via ordering in moves list
        val = du + risk - 0.03 * (do_next - du)
        if val < best_move[0]:
            best_move = (val, dx, dy)

    return [int(best_move[1]), int(best_move[2])]