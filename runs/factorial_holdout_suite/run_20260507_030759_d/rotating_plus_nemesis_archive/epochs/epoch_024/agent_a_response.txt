def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        res.append((rx, ry))
    res.sort()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # Opponent denial heuristic: prefer moves that keep the opponent farther from the best target.
        cur_best = -10**18
        for tx, ty in res:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)

            # If we can reach at same/sooner time than opponent, it's strongly favorable.
            rel = do - ds  # positive means we are closer or tie
            # Add slight preference for closer targets overall.
            val = rel * 1000 - ds

            if val > cur_best:
                cur_best = val

        # Small bias towards staying nearer to current best-resource direction (tie-break stability)
        # also prefers moves with smaller own distance to nearest resource.
        nearest_d = min(man(nx, ny, tx, ty) for tx, ty in res)
        cur = cur_best - nearest_d * 0.01

        if cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]