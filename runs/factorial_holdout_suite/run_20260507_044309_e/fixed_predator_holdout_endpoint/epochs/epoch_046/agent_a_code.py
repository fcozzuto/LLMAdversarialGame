def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_move = [0, 0]

    # Deterministic tie-break order
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        # Pick target: maximize guaranteed lead; if no lead, minimize opponent lead.
        best_target_val = None
        for rx, ry in resources_sorted:
            my_t = cheb(nx, ny, rx, ry)
            op_t = cheb(ox, oy, rx, ry)
            lead = op_t - my_t  # positive means we're faster
            # small secondary terms to prefer nearer resources once comparable
            val = (lead, -my_t, -rx, -ry)
            if best_target_val is None or val > best_target_val:
                best_target_val = val

        # If we can secure some lead, prioritize it strongly; otherwise chase the best attainable.
        # Also add slight bias to keep moving toward center-ish to avoid getting corner-trapped.
        center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        final = (best_target_val[0], best_target_val[1], center_bias, -dxm, -dym)
        if best is None or final > best:
            best = final
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]