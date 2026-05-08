def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target that we can potentially beat (opponent not much closer).
    best_t = None
    best_key = None
    for tx, ty in resources:
        self_d = md(sx, sy, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        lead = opp_d - self_d  # positive => we are closer
        # Prefer immediate closeness if lead is similar; also slightly prefer cells more likely to be on the path
        key = (lead, -self_d)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Evaluate moves by the lead differential after moving, tie-breaking by target distance and safety.
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        lead = opp_d - self_d
        # If we are already on target cell (shouldn't happen often), highest lead anyway; deterministic tie-break by closeness.
        score = (lead, -self_d, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]