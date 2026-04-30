def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obstacle_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 1
        return pen

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Determine a deterministic "frontier" target to reduce symmetry
    # Prefer resources that are closer to our corner than opponent is (global bias).
    my_corner = (0, 0) if (sx + sy) <= (ox + oy) else (W - 1, H - 1)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            # If invalid, engine keeps us in place; score as staying.
            nx, ny = sx, sy
        score = 0
        score -= adj_obstacle_pen(nx, ny) * 0.7

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Big reward if we are strictly closer than opponent after this move.
            # Smaller reward otherwise, still encouraging approaching "contested" resources.
            diff = opd - myd
            # Tie-break to avoid oscillations: prefer resources closer to our chosen corner.
            bias = -0.05 * cheb(my_corner[0], my_corner[1], rx, ry)
            # Prefer immediate capture (distance 0) strongly.
            cap = 50.0 if myd == 0 else 0.0
            # Slightly discourage moving away from all resources.
            score += diff * diff + bias + cap

        # Secondary deterministic tie-break: prefer moves that reduce distance to the single best resource by diff.
        if score > best_val:
            best_val = score
            best_move = (dx, dy)
        elif score == best_val:
            # compare lexicographically by (dx,dy) for determinism
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]