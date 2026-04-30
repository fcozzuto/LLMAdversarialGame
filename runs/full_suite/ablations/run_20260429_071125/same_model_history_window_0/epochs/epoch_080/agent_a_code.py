def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    dirs = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            dirs.append((dx, dy))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Target selection based on "who can reach it sooner" heuristic
    if resources:
        best_res = None
        best_score = -10**18
        for r in resources:
            ds = dist2((sx, sy), r)
            do = dist2((ox, oy), r)
            # Prefer resources we can reach sooner; add slight preference for nearer resources
            score = (do - ds) * 100 - ds
            if score > best_score:
                best_score = score
                best_res = r
        # If we're extremely behind on all resources, shift toward the farthest resource to force tradeoffs
        # (deterministic and materially different from simply chasing the nearest)
        ds_best = dist2((sx, sy), best_res)
        if (min(dist2((sx, sy), r) for r in resources) + 1) < (dist2((ox, oy), best_res)):
            # Choose resource maximizing (our distance - opponent distance) to avoid being consistently outraced
            best_res = None
            best_score = -10**18
            for r in resources:
                ds = dist2((sx, sy), r)
                do = dist2((ox, oy), r)
                score = (ds - do) * 100 - ds
                if score > best_score:
                    best_score = score
                    best_res = r
    else:
        best_res = None

    def position_value(px, py):
        if best_res is not None:
            # Composite: maximize how close we get while keeping opponent further from the same resource
            ds = dist2((px, py), best_res)
            do = dist2((ox, oy), best_res)
            return (do - ds) * 1000 - ds
        # No resources: drift toward center
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        dcen = (px - cx) * (px - cx) + (py - cy) * (py - cy)
        # Also slightly reduce distance to opponent to prevent running out
        d_op = dist2((px, py), (ox, oy))
        return -dcen - 0.001 * d_op

    # Evaluate candidate moves; avoid obstacles; tie-break deterministically by dir order
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = position_value(nx, ny)
        # If moving into a square adjacent to many obstacles, penalize
        adj_obs = 0
        for adx, ady in dirs:
            ax2, ay2 = nx + adx, ny + ady
            if inb(ax2, ay2) and (ax2, ay2) in obstacles:
                adj_obs += 1
        val -= adj_obs * 10
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]