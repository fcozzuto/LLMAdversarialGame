def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas2 = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            deltas2.append((dx, dy))
    if not deltas2:
        return [0, 0]

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas2:
        nx, ny = sx + dx, sy + dy

        # If we can land on a resource immediately, do it.
        immediate = False
        for tx, ty in res:
            if nx == tx and ny == ty:
                immediate = True
                break
        if immediate:
            return [dx, dy]

        # Otherwise, pick the move that maximizes winning chances on some resource.
        # Key: prefer larger (opp_dist - my_dist), then smaller my_dist.
        # Deterministic: also prefer smaller target coords on ties.
        move_best = None
        for tx, ty in res:
            dm = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            win_margin = do - dm
            # Higher win_margin is better; use reverse by negating in lexicographic min.
            key = (-win_margin, dm, tx, ty)
            if move_best is None or key < move_best:
                move_best = key
        if best_key is None or move_best < best_key:
            best_key = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]