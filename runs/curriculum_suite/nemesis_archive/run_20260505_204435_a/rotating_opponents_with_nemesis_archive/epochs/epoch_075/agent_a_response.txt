def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Denial-oriented: pick the move that maximizes advantage over the best resource for us,
    # and simultaneously worsens opponent access to that same resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Prefer moves that keep options open (stay away from dead ends by lightly favoring center)
        center_bias = -cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)

        # Evaluate each resource; choose the target that benefits most under the same-move framework.
        local_best = -10**9
        for (rx, ry) in rpos:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Advantage term: how much closer we are than the opponent.
            # Also discourage moving to resources that opponent is already closer to.
            adv = (opd - myd) * 4
            # If we are far, reduce score; if opponent is far, slightly reward.
            dist_pen = -myd
            denial = -opd * 0.3
            val = adv + dist_pen + denial
            if val > local_best:
                local_best = val
        key = (-(local_best + center_bias), -dx, -dy)  # deterministic tie-break
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]