def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    if unclaimed:
        targets = [tuple(p) for p in unclaimed[:30]]
    # pick a deterministic direction preference biased by opponent
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    dx_to_opp = 0 if ox == sx else (1 if ox > sx else -1)
    dy_to_opp = 0 if oy == sy else (1 if oy > sy else -1)
    preferred = (dx_to_opp, dy_to_opp)
    if preferred in dirs:
        dirs = [preferred] + [d for d in dirs if d != preferred]
    if w <= 0 or h <= 0:
        return [0, 0]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # main goal: approach opponent
        score = -man(nx, ny, ox, oy)
        # secondary goal: approach an unclaimed cell if any
        if targets:
            score += 0.15 * (-min(man(nx, ny, tx, ty) for tx, ty in targets))
        # slight bias to avoid staying still
        if dx == 0 and dy == 0:
            score -= 0.05
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]