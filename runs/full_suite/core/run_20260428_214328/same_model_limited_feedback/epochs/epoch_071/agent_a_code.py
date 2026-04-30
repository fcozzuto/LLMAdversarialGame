def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # Fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0, -10**9]
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                sc = -d
                if sc > best[2]:
                    best = [dx, dy, sc]
        return [best[0], best[1]]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target resource with deterministic tie-breaking
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; slight preference for being farther from opponent (less contested)
        key = (ds - (0.6 * do), ds, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res

    move_order = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18
    # Reward collecting immediately
    target_set = set(tuple(p) for p in resources)

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = manh(nx, ny, tx, ty)
        d_to_o = manh(nx, ny, ox, oy)
        sc = -d_to_t + 0.15 * d_to_o
        if (nx, ny) in target_set:
            sc += 50.0
        # Small deterministic bias toward decreasing Euclidean-ish distance
        eu_bias = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) * 0.01
        sc += eu_bias
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]