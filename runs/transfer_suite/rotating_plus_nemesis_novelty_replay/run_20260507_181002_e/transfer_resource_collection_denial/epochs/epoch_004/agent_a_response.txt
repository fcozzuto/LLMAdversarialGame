def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    max_benefit = None

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        benefit = do - ds  # positive means we are closer
        if max_benefit is None or benefit > max_benefit:
            max_benefit = benefit

    # If we're not ahead anywhere, prioritize moves that improve "us ahead" most after this step.
    # Otherwise, prioritize immediate ahead + closeness.
    want_attack = max_benefit is None or max_benefit >= 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        hit_obstacle = 1 if (nx, ny) in obs else 0

        best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            benefit = do - ds  # after move
            if want_attack:
                # maximize benefit, then minimize our distance, then deterministic
                key = (-benefit, ds, do, rx, ry)
            else:
                # if opponent likely denies, reduce their advantage and avoid getting too close to what they take
                key = (0 if benefit > 0 else 1, -benefit, ds - (do if do < ds else 0), do, rx, ry)
            if best is None or key < best:
                best = key

        # prefer no obstacle hits; then best key
        move_key = (hit_obstacle, best)
        candidates.append((move_key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]