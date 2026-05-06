def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(map(tuple, observation["obstacles"]))
    blocked = obstacles
    best = None

    def dist(a, b, c, d):  # squared euclid
        dx = a - c; dy = b - d
        return dx * dx + dy * dy

    # Select target: nearest resource with deterministic tie-break (distance, then x, then y)
    if resources:
        tx, ty = sorted(resources, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))[0]
    else:
        tx, ty = ox, oy  # fallback: move toward opponent

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # deterministic preference order via sorted moves
    moves.sort()

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        # Reward approaching target, slight repulsion from opponent, small preference for forward progress
        d_to_target = dist(nx, ny, tx, ty)
        d_to_opp = dist(nx, ny, ox, oy)
        score = -d_to_target
        score += 0.35 * min(25, d_to_opp)  # farther from opponent
        # If already on/near target, prioritize taking it
        if d_to_target == 0:
            score += 1000
        # Small bias to reduce distance to opponent's position (helps cut them off occasionally)
        score -= 0.02 * d_to_opp
        # Deterministic tie-break: smaller dx, then dy favor staying/goals
        key = (-score, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]