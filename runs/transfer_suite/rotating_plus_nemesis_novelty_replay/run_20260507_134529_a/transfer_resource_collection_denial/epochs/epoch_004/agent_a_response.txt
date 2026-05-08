def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in observation.get("obstacles") or [])
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    scored = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can front-run; otherwise deny those they are closer to.
        # Tie-break: fewer total steps to improve reliability.
        front = (sd < od)
        gap = od - sd
        scored.append((front, gap, -(sd + od), rx, ry))

    # Deterministic target selection.
    front_targets = [t for t in scored if t[0]]
    pool = front_targets if front_targets else scored
    pool.sort(key=lambda z: (z[0] == False, -z[1], z[2], z[3], z[4]))
    _, _, _, tr_x, tr_y = pool[0]

    # Choose the legal move that most improves our distance to target, but stays away from obstacles.
    def dist_to_target(dx, dy):
        nx, ny = sx + dx, sy + dy
        return cheb(nx, ny, tr_x, tr_y)

    def obstacle_risk(dx, dy):
        nx, ny = sx + dx, sy + dy
        # Count immediate blocked neighbors; lower is better.
        risk = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if (ax, ay) in obstacles:
                    risk += 1
        return risk

    moves.sort(key=lambda m: (dist_to_target(m[0], m[1]), obstacle_risk(m[0], m[1]), m[0], m[1]))
    return [int(moves[0][0]), int(moves[0][1])]