def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))  # deterministic tie behavior

    # Interception-oriented: prefer moves that reduce our distance to resources where we can beat the opponent,
    # and if we can't, reduce their lead as much as possible.
    best_move = (0, 0)
    best_val = None

    # Centering preference to avoid oscillation when tied.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best resource after making this move.
        if resources:
            best_resource_score = None
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)

                # If we can reach sooner, reward heavily; if not, still try to narrow the gap.
                # Also bias toward earlier capture (smaller d_me).
                gap = d_op - d_me
                score = (gap * 10) - d_me

                if best_resource_score is None or score > best_resource_score:
                    best_resource_score = score
            val = best_resource_score
        else:
            # No resources visible: move toward center (stable).
            val = -cheb(nx, ny, int(cx), int(cy))

        # Tie-break: closer to center, then deterministic smallest dx,dy from sorted order.
        tie_center = -cheb(nx, ny, int(cx), int(cy))
        key = (val, tie_center)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]