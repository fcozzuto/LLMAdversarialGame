def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            resources.append((r[0], r[1]))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    # Opponent pressure point: resource where opponent is closest.
    opp_best = None
    opp_best_d = None
    for rx, ry in resources:
        d = manh(ox, oy, rx, ry)
        if opp_best is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best):
            opp_best, opp_best_d = (rx, ry), d
    tx, ty = opp_best

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: maximize advantage over opponent on any resource.
        local_best_lead = -10**9
        local_best_our_d = None
        local_best_opp_d = None
        local_best_cell = None
        for rx, ry in resources:
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            lead = opp_d - our_d
            if (lead > local_best_lead or
                (lead == local_best_lead and (local_best_our_d is None or our_d < local_best_our_d)) or
                (lead == local_best_lead and our_d == local_best_our_d and (rx, ry) < local_best_cell)):
                local_best_lead = lead
                local_best_our_d = our_d
                local_best_opp_d = opp_d
                local_best_cell = (rx, ry)

        # Secondary: if we can't get lead, move to reduce opponent's nearest-resource distance.
        intercept_our_d = manh(nx, ny, tx, ty)
        intercept_opp_d = opp_best_d
        intercept_pressure = intercept_opp_d - intercept_our_d

        # Combine deterministically.
        score = (
            local_best_lead,
            intercept_pressure,
            -local_best_opp_d,
            -local_best_our_d,
            nx,
            ny
        )

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]