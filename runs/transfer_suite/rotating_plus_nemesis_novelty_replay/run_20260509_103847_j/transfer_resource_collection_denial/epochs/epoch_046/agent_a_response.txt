def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    # Prefer resources where we are closer than opponent (or at least not much worse).
    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # value: bigger is better; deterministically tie-break by ds, then coords
        key = (do - ds, -ds, -rx, -ry, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    curds = dist(sx, sy, tx, ty)
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        nds = dist(nx, ny, tx, ty)
        ndo = dist(nx, ny, ox, oy)  # proxy for blocking/positioning
        opp_to_target = dist(ox, oy, tx, ty)

        # Primary: get closer to target; Secondary: reduce opponent distance to target;
        # Tertiary: avoid stagnation; Quaternary: deterministic tie by move coords.
        key = (-nds, -(dist(ox, oy, tx, ty) - opp_to_target), curds - nds, ndo, -dx, -dy)
        # Ensure we prefer actual progress when possible.
        if best_move is None or key > best_key:
            best_move = (dx, dy)
            best_key = key

    if best_move is None:
        # All candidate cells blocked; deterministic fallback: stay.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]