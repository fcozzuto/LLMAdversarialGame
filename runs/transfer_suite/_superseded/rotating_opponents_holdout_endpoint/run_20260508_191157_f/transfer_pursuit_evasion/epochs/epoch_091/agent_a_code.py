def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = observation.get("self_role", "pursuer")
    if role != "pursuer":
        # If roles are reversed, stay near resources (none in this task) and avoid capture by mirroring evasion.
        # With no resources, just run to the farthest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        fc = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = fc
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        nc = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))  # corner closest to opponent
        tx, ty = (ox + nc[0]) // 2, (oy + nc[1]) // 2  # integer midpoint toward that corner

    # Prefer aggressive capture-ish movement: directly reduce distance to opponent,
    # while positioning to cut off the opponent's likely route (toward nearest corner).
    best_score = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue

            d_opp = abs(nx - ox) + abs(ny - oy)
            d_mid = abs(nx - tx) + abs(ny - ty)

            # "Escape pressure": how good our position is against moving toward the nearest corner.
            corner_x, corner_y = (0, 0)
            if (w - 1, h - 1) in corners:  # always true; deterministic to keep minimal branching
                corner_x, corner_y = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            d_to_corner = abs(nx - corner_x) + abs(ny - corner_y)

            # Cheaper to move closer to opponent; also make mid positioning secondary.
            # Tie-break deterministically: prefer larger dx then larger dy toward increasing coordinates.
            score = d_opp * 5 + d_mid * 2 + d_to_corner * 0.3
            tie = (score, -(dx), -(dy))
            if best_score is None or tie < best_score:
                best_score = tie
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]