def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource to race for: maximize (opponent_distance - self_distance).
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        race = od - sd  # >0 means we are closer
        # Prefer winning races; otherwise minimize how far behind we are; then quick + top-left.
        key = (-race, sd, rx + ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Greedily move to reduce distance to target, avoiding obstacles.
    best_move = (0, 0)
    best_md = None
    best_tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        md = man(nx, ny, tx, ty)
        # Tie-breaker: prefer moves that also keep/improve race margin vs opponent.
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        race2 = od2 - sd2
        tie = (-race2, md, abs(dx) + abs(dy), dx, dy)
        if best_md is None or (md < best_md) or (md == best_md and tie < best_tie):
            best_md = md
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]