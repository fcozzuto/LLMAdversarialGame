def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if ok(tx, ty):
                targets.append((tx, ty))

    if not targets:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if ok(sx + dx, sy + dy):
            return [dx, dy]
        best = (0, 0)
        bestv = -10**9
        for dxx, dyy in dirs:
            nx, ny = sx + dxx, sy + dyy
            if ok(nx, ny):
                v = -man(nx, ny, tx, ty)
                if v > bestv:
                    bestv = v
                    best = (dxx, dyy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    # For each move, evaluate the single best target (max advantage), not a global scan.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best = -10**18
        for tx, ty in targets:
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            if opp_d == 0 and self_d > 0:
                # Avoid clearly handing a target if opponent is already on it.
                continue

            # Higher is better:
            # - prioritize targets where we are closer than opponent
            # - break ties by favoring smaller self distance
            # - add slight bias to being able to reach sooner
            advantage = opp_d - self_d
            v = advantage * 1000 - self_d + (1 if self_d == 0 else 0)
            if v > move_best:
                move_best = v

        # Slight preference for staying only when it doesn't lose advantage.
        if move_best > best_score or (move_best == best_score and (dx == 0 and dy == 0)):
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]