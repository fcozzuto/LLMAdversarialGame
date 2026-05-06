def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick an interference target: a resource the opponent is closest to.
    # Then score our immediate move by (we get closer) while (opponent gets not closer).
    def opp_near_score(t):
        return man((ox, oy), t), man((sx, sy), t), t[0], t[1]

    target = min(resources, key=opp_near_score)
    tx, ty = target

    def eval_pos(nx, ny):
        # Favor capturing target and denying nearby alternatives.
        d_self = man((nx, ny), (tx, ty))
        d_opp = man((ox, oy), (tx, ty))
        base = (d_opp - d_self) * 10 - d_self

        # Deny: reduce chance that opponent can instantly choose another close resource.
        # Approx: for each resource, estimate opponent's best option after our move.
        # Weight more toward resources near opponent (resource denial behavior).
        best_gain = -10**9
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                continue
            do = man((ox, oy), (rx, ry))
            ds = man((nx, ny), (rx, ry))
            g = (do - ds)
            if g > best_gain:
                best_gain = g
        base += best_gain * 2

        # Mild obstacle proximity penalty (avoid "stuck" corners).
        adj_pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_pen += 1
        base -= adj_pen
        return base

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = eval_pos(nx, ny)
            if v > best_val or (v == best_val and (dx, dy) < best):
                best_val = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]