def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # Penalize being adjacent to obstacles to reduce getting stuck
    def obstacle_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1
        return pen

    if not resources:
        # Late game: keep away from opponent
        best = [-10**18, 0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            val = d - 0.3 * obstacle_pen(nx, ny)
            if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
                best = [val, dx, dy]
        return [best[1], best[2]]

    # Main: maximize (we get closer) and (we deny opponent) for the best contested resource
    best = [-10**18, 0, 0]
    w_deny = 0.75
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose the resource that gives best net advantage after this move
        best_net = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            net = (-d_self) + w_deny * d_opp
            # small tie-break toward nearer resources overall
            net -= 0.05 * (d_self + d_opp)
            if net > best_net:
                best_net = net
        val = best_net - 0.35 * obstacle_pen(nx, ny)
        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = [val, dx, dy]

    return [best[1], best[2]]