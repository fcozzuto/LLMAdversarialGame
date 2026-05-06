def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource-denial heuristic:
        # Prefer moves that make us closer than the opponent to some resource;
        # otherwise, chase resources the opponent is currently closer to (to contest).
        local_best = None
        for rx, ry in resources:
            d_self = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)

            # If d_self <= d_opp, being closer is strongly good (denial).
            # If we're farther, still prioritize the resources the opponent values (small contest term).
            delta = d_opp - d_self  # positive => we are closer than opponent at this next step
            contested = -d_self + 0.6 * delta  # always encourages reaching; denial boosts when we can beat opponent

            # Slight tie-break toward reducing absolute distance to any resource.
            key_val = contested - 0.05 * d_opp
            if local_best is None or key_val > local_best:
                local_best = key_val

        # Small preference for staying mobile: penalize staying only if equal scores exist.
        stay_pen = -0.001 if (dx, dy) == (0, 0) else 0.0
        val = (local_best + stay_pen) if local_best is not None else -10**9

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]