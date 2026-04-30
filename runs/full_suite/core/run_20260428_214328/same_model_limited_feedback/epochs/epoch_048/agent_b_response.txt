def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set((p[0], p[1]) for p in (observation["obstacles"] or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_delta = (0, 0)
    best_val = -10**18

    if not resources:
        # drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                val = -(cheb(nx, ny, cx, cy))
                if val > best_val:
                    best_val = val
                    best_delta = (dx, dy)
        return [best_delta[0], best_delta[1]]

    # Pre-filter resources blocked by obstacles (if any)
    res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res:
        return [0, 0]

    # Deterministic tie-break: prefer lexicographically smaller delta among equal values
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Choose the best resource for this step
        step_val = -10**18
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            osd = cheb(ox, oy, rx, ry)
            # Favor reaching quickly and denying the opponent proximity
            val = (-ds) + (0.65 * osd)
            # slight preference toward nearer resources to the opponent's current position line
            if ds == 0:
                val += 5.0
            if val > step_val:
                step_val = val
        # If multiple moves target similar resources, add small bias toward reducing distance to the best resource type
        # Bias by closeness to nearest resource
        min_ds = min(cheb(nx, ny, rx, ry) for (rx, ry) in res)
        step_val += (-0.05 * min_ds)
        if step_val > best_val or (step_val == best_val and (dx, dy) < best_delta):
            best_val = step_val
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]