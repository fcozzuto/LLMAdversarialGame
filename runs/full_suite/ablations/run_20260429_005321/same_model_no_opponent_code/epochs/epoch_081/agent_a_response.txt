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

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target where we are not worse than opponent (when possible).
    my_opp_better = []
    for r in resources:
        if cheb((sx, sy), r) <= cheb((ox, oy), r):
            my_opp_better.append(r)
    pool = my_opp_better if my_opp_better else resources

    target = min(pool, key=lambda r: (cheb((sx, sy), r), r[1], r[0]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Precompute obstacle adjacency to discourage squeezing near obstacles.
    adj_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = cheb((nx, ny), target)
        opp_d = cheb((nx, ny), (ox, oy))

        # Obstacle proximity penalty
        prox = 0
        for ax, ay in adj_offsets:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                prox += 1

        # Prefer progress to target, keep distance from opponent, avoid obstacle clutter.
        score = (-my_d * 1000) + (opp_d * 8) - (prox * 2) + ((nx - sx) * 1 + (ny - sy) * 0)
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]