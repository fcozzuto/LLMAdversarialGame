def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    blocked = set()
    for p in observation.get("obstacles", []):
        try:
            x, y = p[0], p[1]
            blocked.add((x, y))
        except Exception:
            pass

    resources = observation.get("resources", [])
    res_pos = []
    for r in resources:
        try:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_pos.append((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    if res_pos:
        # Pick the nearest resource to us as a target (deterministic).
        target = min(res_pos, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

        tx, ty = target
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in blocked:
                continue
            # Prefer decreasing Manhattan distance to target; break ties deterministically.
            d = abs(tx - nx) + abs(ty - ny)
            val = -d
            if dx == 0 and dy == 0:
                val -= 0.01  # slight penalty to avoid staying
            # Small deterministic tiebreak toward opponent direction (harmless if opponent irrelevant).
            val += (nx - ox) * 1e-6 - (ny - oy) * 1e-6
            if val > best_val:
                best_val = val
                best = [dx, dy]

        if best is not None:
            return best

    # If no resources or no legal move toward them: try to avoid opponent; else stay.
    best = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in blocked:
            continue
        d_opp = abs(ox - nx) + abs(oy - ny)
        # Prefer maximizing distance; deterministic tie-break.
        val = d_opp + (dx == 0 and dy == 0) * 0.001
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best