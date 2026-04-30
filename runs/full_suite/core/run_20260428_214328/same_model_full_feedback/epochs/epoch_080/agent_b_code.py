def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def target_score(px, py):
        if resources:
            best = 10**9
            for rx, ry in resources:
                d = cheb(px, py, rx, ry)
                if d < best:
                    best = d
            return best
        return cheb(px, py, (w - 1) // 2, (h - 1) // 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    base_opp = cheb(sx, sy, ox, oy)
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        on_res = (nx, ny) in set(resources)
        dist_res = target_score(nx, ny)
        opp_dist = cheb(nx, ny, ox, oy)
        # Prefer collecting, then approaching nearest resource, while staying away from opponent.
        val = 0
        if on_res:
            val += 10**7
        val -= dist_res * 1000
        val += opp_dist * 3
        # Small deterministic tie-break: prefer moves that reduce distance to opponent.
        val -= abs((opp_dist - base_opp)) * 0.1
        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move