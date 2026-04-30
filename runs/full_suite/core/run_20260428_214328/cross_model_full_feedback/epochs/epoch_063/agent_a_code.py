def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y): obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist_cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Choose a contestable target: prefer resources we reach relatively sooner than opponent
    target = None
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            # Encourage taking when we're clearly closer; break ties by absolute distance
            key = (d - 0.95 * od, d, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best

    # Fallback: move toward center
    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        ns = (nx, ny)
        d_self = dist_cheb(ns, (tx, ty))
        d_opp = dist_cheb(ns, (ox, oy))
        # Primary: reduce distance to target; Secondary: keep away from opponent a bit; Tertiary: deterministic order
        key = (d_self, -0.03 * d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]