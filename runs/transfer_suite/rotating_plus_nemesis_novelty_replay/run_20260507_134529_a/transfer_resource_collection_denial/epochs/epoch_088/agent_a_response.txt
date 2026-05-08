def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))
    blocked = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if not resources:
            # Fall back: head toward opponent's corner (likely sweep path), while staying close to opponent to deny.
            nd = man(nx, ny, w - 1, h - 1) if (ox, oy) == (0, 0) else man(nx, ny, 0, 0)
            od = man(ox, oy, w - 1, h - 1) if (ox, oy) == (0, 0) else man(ox, oy, 0, 0)
            score = (od - nd) - 0.01 * nd
        else:
            # Choose the move maximizing advantage to the best reachable resource.
            # Add small tie-break to prefer closer absolute resource and moving toward our preferred direction (diagonal preference).
            score = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Higher when we are closer than opponent; scale slightly with fewer resources remaining.
                s = (od - sd) + (0.02 * (1 if remaining <= 6 else 0)) - 0.01 * sd
                if score is None or s > score:
                    score = s
            # Extra deterministic tie-break: reduce distance to nearest resource overall.
            mind = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if mind is None or d < mind:
                    mind = d
            score = score - 0.0001 * mind

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move