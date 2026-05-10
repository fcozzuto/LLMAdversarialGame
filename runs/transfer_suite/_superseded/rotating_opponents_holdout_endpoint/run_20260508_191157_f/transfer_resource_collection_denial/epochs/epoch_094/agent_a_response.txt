def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        best = None
        best_key = None
        for x, y in resources:
            sd = manhattan(x, y, sx, sy)
            od = manhattan(x, y, ox, oy)
            # Prefer reachability; then prefer states where we are relatively closer.
            key = (-(sd - od), sd, od, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y, sd, od)
        return best

    tx, ty, sd, od = best_target()

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                sd_a = manhattan(nx, ny, tx, ty)
                od_a = manhattan(ox, oy, tx, ty)
                legal.append((dx, dy, nx, ny, sd_a, od_a))

    if not legal:
        return [0, 0]

    # If opponent is not worse for the chosen target, choose a "steal" move to minimize opponent gap.
    if od <= sd:
        best = None
        best_key = None
        for dx, dy, nx, ny, sd_a, od_a in legal:
            # We want sd_a - od_a to be as small/negative as possible; tie-break by progress to target.
            key = (sd_a - od_a, sd_a, -manhattan(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Otherwise advance toward the target, with small bias away from opponent to reduce interception risk.
    best = None
    best_key = None
    for dx, dy, nx, ny, sd_a, od_a in legal:
        key = (sd_a, -manhattan(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]