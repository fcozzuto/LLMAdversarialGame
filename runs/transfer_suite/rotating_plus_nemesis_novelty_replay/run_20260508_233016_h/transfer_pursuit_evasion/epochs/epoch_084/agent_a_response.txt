def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Deterministic preference order:
    # - For pursuer: minimize manhattan distance, then maximize "alignment" to reduce escape.
    # - For evader: maximize manhattan distance, then maximize angular separation by preferring steps that
    #   increase dot product with vector away from pursuer.
    best_move = [0, 0]
    best_val = None

    vx, vy = (sx - ox), (sy - oy)  # away vector
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)

        # alignment score based on dot of move relative to away direction
        # pursuer tries to reduce dist; evader tries to increase dist.
        # Use dot with away vector for evader; opposite for pursuer to "push" toward pursuer.
        mdx, mdy = dx, dy
        dot_away = mdx * vx + mdy * vy

        # Secondary heuristic to avoid cornering into obstacles: prefer staying closer to center if tie.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(nx - cx) + abs(ny - cy)

        if evader:
            # maximize dist, then dot_away, then center_pen (smaller is better)
            val = (dist, dot_away, -center_pen)
        else:
            # minimize dist, then dot_away (negative helps, so maximize -dist already implicit by tuple)
            # Use (-dist, dot_away, -center_pen) to maximize tuple deterministically.
            val = (-dist, -dot_away, -center_pen)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move