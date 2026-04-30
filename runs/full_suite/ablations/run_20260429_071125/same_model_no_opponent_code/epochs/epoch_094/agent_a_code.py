def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            self_pos = (nx, ny)
            # Maximize relative advantage: opponent gets farther than us (for the best resource)
            rel_best = -10**18
            for r in resources:
                rel = man((ox, oy), r) - man(self_pos, r)
                # Prefer resources we can reach sooner, but keep determinism
                tieb = -man(self_pos, r)
                v = rel * 1000 + tieb
                if v > rel_best:
                    rel_best = v
            # Small center bias to break ties consistently
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            val = rel_best + int(center_bias * 0.01)
        else:
            # No resources visible: move to maximize distance from opponent (deterministic tie-breaker)
            d_self = abs(nx - ox) + abs(ny - oy)
            val = d_self * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]