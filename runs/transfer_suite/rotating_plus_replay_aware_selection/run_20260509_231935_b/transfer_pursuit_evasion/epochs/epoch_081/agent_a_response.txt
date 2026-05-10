def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if observation.get("resources") is None:
        resource_targets = []
    else:
        resource_targets = []
        for r in (observation.get("resources", []) or []):
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                    resource_targets.append((x, y))

    target_list = resource_targets if resource_targets else ([ox, oy] and [(ox, oy)])
    if not pursuer:
        target_list = corners

    def score(nx, ny):
        if pursuer:
            tx, ty = (target_list[0] if resource_targets else (ox, oy))
            d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            # primary: minimize distance to opponent; secondary: gently bias toward resources (if any)
            return d_op * 100000 + d_t
        else:
            d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # primary: maximize distance from pursuer; secondary: keep toward farthest corner from pursuer
            fx, fy = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
            d_corner = (fx - nx) * (fx - nx) + (fy - ny) * (fy - ny)
            return -(d_op * 100000 + d_corner)

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            sc = score(nx, ny)
            if best is None or sc < best:
                best, best_move = sc, (dx, dy)
    return [best_move[0], best_move[1]]