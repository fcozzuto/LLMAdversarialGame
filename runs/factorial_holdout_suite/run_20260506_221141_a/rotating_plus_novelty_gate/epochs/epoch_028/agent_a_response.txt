def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not resources:
        return [0, 0]

    def steps(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Strategic selection:
    # - If we can reach a resource first (positive advantage), pick the best advantage.
    # - Otherwise (opponent closer), pick the resource that is most urgent for us to contest
    #   (min opponent distance, while still being reasonably close to us).
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
            continue
        ds = steps(sx, sy, tx, ty)
        do = steps(ox, oy, tx, ty)
        adv = do - ds  # positive means we are closer/equal in steps
        # quadrant bias: push away from opponent by preferring opposite corner direction
        quad = (1 if tx < w - 1 else 0) + (1 if ty < h - 1 else 0)
        # When contesting, also bias towards resources nearer our side to reduce interception time.
        key_contest = (-do, ds, -(tx + ty), -quad)
        key_take = (adv, -ds, -((tx + ty) & 1), -tx, -ty)
        if adv >= 0:
            key = ("take",) + key_take
        else:
            key = ("contest",) + key_contest
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dself = steps(nx, ny, tx, ty)
        dopp = steps(ox, oy, tx, ty)
        adv_after = dopp - dself
        v = (adv_after, -dself, -((nx + ny) & 1), -dx, -dy)
        if bestv is None or v > bestv:
            bestv = v
            bestm = [dx, dy]

    return [int(bestm[0]), int(bestm[1])]