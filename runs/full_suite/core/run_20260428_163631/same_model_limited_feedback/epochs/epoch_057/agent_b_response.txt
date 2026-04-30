def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose contested target: prioritize resources where we are relatively closer.
    target = None
    best = None
    if resources:
        for r in resources:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            val = ds - do  # lower means we are more ahead on that resource
            if best is None or val < best:
                best = val
                target = r
            elif val == best and (ds < dist((sx, sy), target)):
                target = r
    else:
        target = (w // 2, h // 2)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_mv = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dself = dist((nx, ny), target)
        dop = dist((ox, oy), target)
        # If near tie, prefer moves that don't let opponent get dramatically closer.
        opp_adv = dist((ox, oy), (nx, ny))
        score = (dself, -dop, opp_adv)
        if best_score is None or score < best_score:
            best_score = score
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]