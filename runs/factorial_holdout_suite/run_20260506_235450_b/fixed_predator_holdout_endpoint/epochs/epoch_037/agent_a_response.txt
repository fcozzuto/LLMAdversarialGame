def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Evaluate next position: best achievable "margin" (opponent farther than us) with tie-break by closeness.
    def eval_pos(px, py):
        best_m = None
        best_sd = None
        for rx, ry in res:
            sd = abs(px - rx) + abs(py - ry)
            od = abs(ox - rx) + abs(oy - ry)
            m = od - sd
            if best_m is None or m > best_m or (m == best_m and sd < best_sd):
                best_m, best_sd = m, sd
        # small preference to move closer overall to the chosen best resource
        return (best_m if best_m is not None else -10**9, -best_sd if best_sd is not None else -10**9)

    best_move = [0, 0]
    best_val = None
    # Deterministic tie-breaking: fixed dir order and then prefer staying still only if equal.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = eval_pos(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = [dx, dy]
    return best_move