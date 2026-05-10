def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick the best contest target: maximize opponent advantage against us (od - sd),
    # i.e., prefer resources where we are not slower, then closer/with stable tie-break.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (-(od - sd), sd, (rx + ry))  # smaller is better for first two terms
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Evaluate each move by the improvement in our contest over the best remaining target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Race score: for each resource, compare our distance to opponent's.
        # Use max over resources of (od - sd) after the move; higher means we are relatively closer.
        best_race = None
        closest = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            race = od - sd
            if best_race is None or race > best_race:
                best_race = race
            d = sd
            if closest is None or d < closest:
                closest = d

        # Tie-break: prefer reaching something sooner; slight bias toward moving toward chosen target.
        to_target = man(nx, ny, rx, ry)
        val = (best_race, -closest, -to_target)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]