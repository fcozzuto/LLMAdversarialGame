def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    def xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default
    sx, sy = xy(observation.get("self_position", None), (0, 0))
    ox, oy = xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        x, y = xy(r, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (-10**9, None, 0, 0)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        local_best = (-10**9, 10**9)
        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            advantage = (do - ds)  # want us closer than opponent after move
            # prefer contesting when opponent is near/close; also prefer immediate pickup
            bonus = 6 if ds == 0 else 0
            contest = 3 if advantage > 0 else -1
            # small preference for reducing our distance to the target
            val = advantage * 10 + bonus + contest - ds
            if val > local_best[0] or (val == local_best[0] and ds < local_best[1]):
                local_best = (val, ds)

        # also discourage moves that let opponent reach the best resource sooner by one step
        # (approx) using the same best resource distance comparisons
        score = local_best[0]
        if score > best[0]:
            best = (score, (dx, dy), local_best[1], 0)

    return [int(best[1][0]), int(best[1][1])]