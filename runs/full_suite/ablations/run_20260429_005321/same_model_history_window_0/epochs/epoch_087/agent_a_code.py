def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # No visible resources: drift toward center to avoid being cornered
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            d1 = abs(rx - sx) + abs(ry - sy)
            d2 = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach sooner; slight bias toward closer overall
            score = (d2 - d1, -(d1 + d2))
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: fixed move order above
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; also avoid stepping into proximity of opponent
        to_t = abs(tx - nx) + abs(ty - ny)
        opp_close = abs(ox - nx) + abs(oy - ny)
        val = (-to_t, opp_close)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]