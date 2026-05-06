def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    best = None
    # Evaluate by trying to become (or stay) closer than the opponent to the same resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        best_for_move = None
        for rx, ry in resources:
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            # Prefer smaller "we are closer margin"; tie-break by reaching sooner, then resource coordinates.
            key = (our_d - opp_d, our_d, rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key

        # Also discourage moves that increase our distance to the closest resource overall.
        closest_after = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        score = (best_for_move[0], best_for_move[1], closest_after, dx, dy)
        if best is None or score < best:
            best = score

    if best is None:
        return [0, 0]
    return [best[3], best[4]]