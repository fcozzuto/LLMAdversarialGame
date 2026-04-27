def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", []) or []
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    if not resources:
        dx = -1 if ox < sx else (1 if ox > sx else 0)
        dy = -1 if oy < sy else (1 if oy > sy else 0)
        tx, ty = sx + dx, sy + dy
        if inside(tx, ty) and (tx, ty) not in obstacles:
            return [dx, dy]
        return [0, 0]
    # If already on a resource, stay to allow pickup.
    for rx, ry in resources:
        if rx == sx and ry == sy and (sx, sy) not in obstacles:
            return [0, 0]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate by best resource tradeoff (closer to us, farther from opponent).
        best_here = -10**9
        for rx, ry in resources:
            d_us = dist((nx, ny), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            val = (20 - d_us) - 0.7 * d_op
            # Small bias to prefer moving toward board center early.
            center_bias = -0.02 * (abs((w-1)/2 - nx) + abs((h-1)/2 - ny))
            if val + center_bias > best_here:
                best_here = val + center_bias
        # Prefer capturing sooner: higher gradient for small distances.
        if best_here == -10**9:
            continue
        if best is None or best_here > best:
            best = best_here
            best_move = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]