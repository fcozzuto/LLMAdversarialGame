def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            res.append((px, py))
            resset.add((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # If we can see resources, compete on them; otherwise drift to center while keeping distance from opponent.
    if res:
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            if (nx, ny) in resset:
                # Strongly prefer immediate pickup, but still consider opponent threat.
                s = 10**12 - md(nx, ny, ox, oy) * 10
            else:
                # Evaluate best target from the new position.
                s = 0
                my_best = 10**9
                op_best = 10**9
                for tx, ty in res:
                    d1 = md(nx, ny, tx, ty)
                    d2 = md(ox, oy, tx, ty)
                    if d1 < my_best:
                        my_best = d1
                    if d2 < op_best:
                        op_best = d2
                # Prefer being closer than opponent; penalize moving into their races.
                lead = op_best - my_best  # positive if we are closer to some resource than opponent
                s = lead * 1000 - my_best * 10
                # Avoid getting too close to opponent unless it wins resources.
                s -= md(nx, ny, ox, oy) * 2
            # Small deterministic tie-break on move "lexicographic" order already stable; but ensure strictness.
            if s > best_score:
                best_score = s
                best_move = [dx0, dy0]
    else:
        cx, cy = w // 2, h // 2
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            # Go to center while not colliding into opponent (keep distance)
            s = -md(nx, ny, cx, cy) * 10 + md(nx, ny, ox, oy) * 2
            if s > best_score:
                best_score = s
                best_move = [dx0, dy0]

    return [int(best_move[0]), int(best_move[1])]