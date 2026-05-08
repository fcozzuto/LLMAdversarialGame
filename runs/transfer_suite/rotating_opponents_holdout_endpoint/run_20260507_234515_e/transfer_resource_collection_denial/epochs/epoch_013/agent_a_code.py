def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Collect if already on a resource
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # Evaluate best target from this candidate position:
        # maximize (opponent_advantage_reduction) while favoring quick collection.
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we can reach sooner, strong positive; if later, negative.
            val = (od - sd) * 1000 - sd * 5 + od
            if val > local_best:
                local_best = val

        # Small tie-break: prefer moves that move closer to the currently best target estimate.
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]