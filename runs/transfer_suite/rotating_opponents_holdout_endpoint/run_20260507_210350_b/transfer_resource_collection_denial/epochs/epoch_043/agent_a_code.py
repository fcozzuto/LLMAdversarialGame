def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    # Pick a resource where we are relatively closer than the opponent (deterministic tie-breaks).
    best_key = None
    best_res = None
    for r in resources:
        self_d = abs(r[0] - sx) + abs(r[1] - sy)
        opp_d = abs(r[0] - ox) + abs(r[1] - oy)
        key = (-(opp_d - self_d), self_d, r[0], r[1])  # maximize (opp-self) via negative
        if best_key is None or key < best_key:
            best_key = key
            best_res = r

    tx, ty = best_res

    # Choose the move that best improves our advantage for the chosen resource.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # Prefer smaller self distance; break ties by larger opponent disadvantage; then lexicographic move.
        val = (self_d, (self_d - opp_d), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves invalid (shouldn't happen), stay.
    return best_move if best_move is not None else [0, 0]