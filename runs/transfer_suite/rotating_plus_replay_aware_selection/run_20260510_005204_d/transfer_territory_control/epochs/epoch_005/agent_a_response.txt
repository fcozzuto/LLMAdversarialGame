def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_set = set(tuple(p) for p in observation.get("self_territory", []))
    opp_set = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_dx = ox - sx
    opp_dy = oy - sy
    main_axis = 0
    if abs(opp_dx) >= abs(opp_dy):
        main_axis = 0 if opp_dx == 0 else (1 if opp_dx > 0 else -1)
    else:
        main_axis = 0  # placeholder for tie; scoring uses both distances anyway

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            type_score = 100.0
        elif (nx, ny) in unclaimed:
            type_score = 20.0
        elif (nx, ny) in self_set:
            type_score = 1.0
        else:
            type_score = 3.0

        # Encourage progress and cutting off opponent: reduce distance to opponent.
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_self = (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy)

        # Prefer moves that improve relative position towards opponent.
        improve = ((sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)) - d_opp

        # Slightly prefer edge expansion when it doesn't require extra distance.
        on_edge = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0

        score = type_score + 2.5 * improve - 0.6 * d_opp - 0.2 * d_self + 0.8 * on_edge

        # Tie-break deterministically by move order.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [int(dx), int(dy)]

    if best_score is None:
        return [0, 0]
    return best_move