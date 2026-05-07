def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Score: pick best target resource for this move
        # Advantage = opponent_distance - our_distance (higher means we are closer)
        # Add bias toward immediate capture and toward reducing opponent's best advantage.
        move_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0:
                base = 1000000  # immediate collection
            else:
                base = (do - ds) * 1000  # primary
                base -= ds  # mild preference for nearer even if tied

            # Encourage denying: if we are not winning, penalize a lot more
            if do - ds <= 0:
                base -= 5000

            # Small preference for resources that are generally closer for us (avoid wandering)
            base -= man(sx, sy, rx, ry) * 2

            if base > move_score:
                move_score = base

        # Secondary: reduce distance to our current best-likely resource (deterministic smoothing)
        # Compute our overall nearest resource distance after move.
        nearest = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = man(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
        move_score -= nearest * 3

        if move_score > best_score:
            best_score = move_score
            best = [dx, dy]

    return best