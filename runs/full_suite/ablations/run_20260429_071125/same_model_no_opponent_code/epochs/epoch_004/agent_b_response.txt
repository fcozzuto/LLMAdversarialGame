def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2): return max(abs(x1 - x2), abs(y1 - y2))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Target value: prefer resources we can reach sooner than opponent, with a slight bias away from opponent corner.
    if resources:
        opp_corner = (w - 1, h - 1) if (ox > (w - 1) / 2 and oy > (h - 1) / 2) else (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        if not resources:
            tx, ty = w // 2, h // 2
            sc = -cheb(nx, ny, tx, ty)
        else:
            best_r_val = None
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # If we are closer, reward; if opponent closer, penalize heavily.
                corner_bias = 0.02 * cheb(opp_corner[0], opp_corner[1], rx, ry)
                val = (d_op - d_my) - 0.12 * d_my + corner_bias
                if best_r_val is None or val > best_r_val:
                    best_r_val = val
            sc = best_r_val

        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    # Deterministic fallback: move toward whichever corner is farther from opponent.
    if best_score is None:
        far_corner = (0, 0) if cheb(ox, oy, 0, 0) >= cheb(ox, oy, w - 1, h - 1) else (w - 1, h - 1)
        tx, ty = far_corner
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]