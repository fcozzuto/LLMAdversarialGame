def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Deterministic fallback: move toward opponent's corner to potentially block indirectly
        tx, ty = (w - 1, h - 1) if (sx + sy) <= ((w - 1 - sx) + (h - 1 - sy)) else (0, 0)
        best = (-10**18, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, tx, ty)
            # Prefer smaller distance; deterministic tie-break by position
            val = -dist * 1000 - (nx * 10 + ny)
            if val > best[0]:
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    best_score = -10**18
    best_move = (0, 0)
    # Evaluate each move by the best resource we can contest immediately
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_best = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Higher is better: we want resources where we are closer than opponent
            # Add small deterministic bias to prefer certain coordinates when tied
            lead = d_opp - d_self
            val = lead * 1000 - (abs(rx - nx) + abs(ry - ny))
            if val > move_best:
                move_best = val
            elif val == move_best:
                # deterministic tie-break: smaller coordinate sum
                if (rx + ry) < (best_move[0] + best_move[1]):  # arbitrary stable tie
                    move_best = val
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]