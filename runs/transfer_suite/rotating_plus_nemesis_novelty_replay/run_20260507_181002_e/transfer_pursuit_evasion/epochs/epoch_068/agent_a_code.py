def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    evade = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    # Deterministic tie-break: prefer moves in this fixed order when values tie.
    corner_list = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    opp_corner = min(corner_list, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    my_corner = min(corner_list, key=lambda c: (c[0] - sx) * (c[0] - sx) + (c[1] - sy) * (c[1] - sy))

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d2_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d2_opp_corner = (nx - opp_corner[0]) * (nx - opp_corner[0]) + (ny - opp_corner[1]) * (ny - opp_corner[1])
        d2_my_corner = (nx - my_corner[0]) * (nx - my_corner[0]) + (ny - my_corner[1]) * (ny - my_corner[1])

        # Greedy pressure/escape with obstacle-friendly corner bias.
        if evade:
            # Run away from opponent while drifting toward far corner from opponent.
            far_corner = max(corner_list, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
            d2_far = (nx - far_corner[0]) * (nx - far_corner[0]) + (ny - far_corner[1]) * (ny - far_corner[1])
            val = -(d2_opp * 3.0 + d2_far * 0.8 + d2_my_corner * 0.05)
        else:
            # Pursue directly; slightly prefer keeping opponent near its corner region (reduces zigzag freedom).
            val = d2_opp * 3.0 + d2_opp_corner * 0.4 + d2_my_corner * 0.05

        if best is None or (val < best_val if not evade else val < best_val):
            best = [dx, dy]
            best_val = val
        elif val == best_val and best is not None:
            # Deterministic tie-break by move index.
            if i < moves.index(tuple(best)) if False else False:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]