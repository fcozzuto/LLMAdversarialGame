def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # No resources: move away from opponent if possible
        candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (-(10**9), 0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]
    # Pick nearest resource; tie-break deterministically
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best_res = None
    best_rd = 10**9
    for r in resources:
        rd = dist((sx, sy), tuple(r))
        if rd < best_rd or (rd == best_rd and (r[0], r[1]) < (best_res[0], best_res[1])):
            best_rd = rd
            best_res = tuple(r)
    tx, ty = best_res
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer moves that reduce distance to target; then maximize distance from opponent; then deterministic tie-break
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Score: lower d_to better, higher d_op better
        score = (-d_to, d_op)
        key = (score, dx, dy)
        if best is None or key > best:
            best = key
    if best is None:
        return [0, 0]
    return [best[1], best[2]]