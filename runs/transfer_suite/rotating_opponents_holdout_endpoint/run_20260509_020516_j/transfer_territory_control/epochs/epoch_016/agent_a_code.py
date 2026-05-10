def choose_move(observation):
    W = int(observation.get("grid_width") or 0)
    H = int(observation.get("grid_height") or 0)
    if W <= 1 or H <= 1:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return 0, 0

    sx, sy = xy(observation.get("self_position") or (0, 0))
    ox, oy = xy(observation.get("opponent_position") or (W - 1, H - 1))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            resources.append((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        x, y = xy(p)
        if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
            unclaimed.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        best = None
        bd = 10**18
        for x, y in resources:
            d = man(sx, sy, x, y)
            if d < bd or (d == bd and (x, y) < best):
                bd = d
                best = (x, y)
        target = best
    elif unclaimed:
        best = None
        bd = 10**18
        for x, y in unclaimed:
            d = man(sx, sy, x, y) + (W * H if (x, y) == (ox, oy) else 0)
            if d < bd or (d == bd and (x, y) < best):
                bd = d
                best = (x, y)
        target = best
    else:
        target = (0 if sx > W // 2 else W - 1, 0 if sy > H // 2 else H - 1)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if target is not None:
            score += -man(nx, ny, target[0], target[1])
        score += man(nx, ny, ox, oy)  # prefer moving away
        # small deterministic tie-breaker: prefer not staying if equal
        if (dx, dy) == (0, 0):
            score -= 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]