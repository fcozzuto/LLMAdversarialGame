def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves.append((0, 0))

    # Choose target giving maximal advantage: opp_dist - self_dist (higher is better).
    tx, ty = None, None
    if resources:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            # Tie-break by smaller self distance then larger opponent distance.
            cand = (adv, -ds, do)
            if best is None or cand > best:
                best = cand
                tx, ty = rx, ry
    if tx is None:
        # No resources shown: go toward center-ish (deterministic).
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        # Prefer approaching target, keep opponent away, and reduce unnecessary steps.
        # Also slightly penalize moving closer to obstacles is implicit via validity; no need extra.
        score = (-(ds), do - ds, - (abs(dx) + abs(dy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]