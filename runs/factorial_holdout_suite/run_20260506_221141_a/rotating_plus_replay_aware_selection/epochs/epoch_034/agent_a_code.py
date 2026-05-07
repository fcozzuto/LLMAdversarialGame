def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if resources:
        on_res = (sx, sy) in set((r[0], r[1]) for r in resources)
        if on_res:
            # Hold unless another move immediately beats current best target
            best_cell = None
        best_val = -10**18
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Prefer moves that secure a resource (opponent slower), and secondarily minimize our time.
            local_best = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Larger is better: secure first, then closeness.
                v = (do - ds) * 10 - ds
                # Mild tie-break toward center to reduce oscillation.
                center_bonus = - (abs(nx - (gw - 1) / 2.0) + abs(ny - (gh - 1) / 2.0)) * 0.01
                v += center_bonus
                if v > local_best:
                    local_best = v
                    best_cell = (rx, ry)
            # If we are already on a resource, keep move unless it helps secure a better one.
            if resources and (sx, sy) in set((r[0], r[1]) for r in resources) and best_move == [0, 0]:
                if local_best < best_val + 1e-9:
                    continue
            if local_best > best_val + 1e-9:
                best_val = local_best
                best_move = [dx, dy]
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift toward the middle while avoiding obstacles.
    cx, cy = (gw - 1) // 2, (gh - 1) // 2
    best_d = 10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if d < best_d:
            best_d = d
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]