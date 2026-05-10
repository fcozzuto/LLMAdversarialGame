def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best_dxdy = (0, 0)
    best_val = None

    any_we_are_closer = False
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        if man(sx, sy, rx, ry) <= man(ox, oy, rx, ry):
            any_we_are_closer = True
            break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose the move that best matches our role:
        # - If we can be closer to some resource, prioritize maximizing advantage (opp farther).
        # - Otherwise, prioritize minimizing opponent's access by heading toward opponent-closest resources.
        best_for_move = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)

            # Advantage: positive when we are closer.
            adv = op_d - my_d
            # Strongly penalize moves that let opponent be strictly closer to the target.
            deny_pen = 12 if op_d < my_d else 0

            # Robustness to opponent: consider how quickly opponent could reach that target.
            # Lower opponent distance is worse for us, so subtract a term with op_d.
            if any_we_are_closer:
                val = (adv * 10) - deny_pen - op_d * 1.0 - my_d * 0.15
            else:
                # Intercept mode: reduce opponent's closest target distance.
                # Prefer targets where opponent is currently close and we can move to them efficiently.
                val = (-op_d * 12) + (my_d <= op_d) * (adv * 6) - deny_pen - my_d * 0.2

            if best_for_move is None or val > best_for_move:
                best_for_move = val

        if best_for_move is None:
            continue

        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_dxdy = (dx, dy)
        elif best_for_move == best_val:
            # Deterministic tie-break: prefer staying, then lexicographically smallest (dx,dy) in dirs order.
            if (dx, dy) == (0, 0):
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]