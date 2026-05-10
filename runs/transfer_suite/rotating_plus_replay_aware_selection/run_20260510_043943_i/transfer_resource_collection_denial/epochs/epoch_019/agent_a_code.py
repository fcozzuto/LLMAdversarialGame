def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no visible resources, drift to corner away from opponent while avoiding obstacles
    if not resources:
        target = (0, 0) if (sx + sy) > (w - 1 - ox + h - 1 - oy) else (w - 1, h - 1)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (man(nx, ny, target[0], target[1]) * 0.1) - man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource scoring: prefer cells with tempo advantage, and punish resources likely contested by sweep-like opponent
    r_left = observation.get("remaining_resource_count", len(resources)) or len(resources)
    finish_phase = 1 if r_left <= 4 else 0
    lambda_row = 2.0 + 0.5 * finish_phase
    lambda_close = 1.2 + 0.8 * finish_phase

    # pick best resource deterministically
    best_cell = None
    best_score = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)

        # sweep_rows-like contest: opponent strongly favors resources on/near its row (same y)
        row_pen = (1 if ry == oy else 0) + (0.5 if abs(ry - oy) == 1 else 0)

        # advantage to win collection first; also prefer nearer when finishing
        score = (od - sd) - lambda_row * row_pen - lambda_close * (sd / max(1, (r_left + 1)))
        # tie-break deterministically: smaller sd, then smaller od, then lexicographic
        if (score > best_score) or (score == best_score and (sd, od, rx, ry) < (man(sx, sy, best_cell[0], best_cell[1]), man(ox, oy, best_cell[0], best_cell[1]), best_cell[0], best_cell[1])):
            best_score = score
            best_cell = (rx, ry)

    tx, ty = best_cell

    # One-step move toward target with obstacle avoidance; also prevent stepping into opponent-adjacent squares
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Avoid being immediately adjacent to opponent to reduce contest collisions
        danger = 1 if d_opp <= 1 else 0
        # small preference for reducing distance while keeping safe
        val = (-(d_to_t) * 2.0) + (d_opp * 0.4) - danger * 3.0
        if (val > best_val) or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]