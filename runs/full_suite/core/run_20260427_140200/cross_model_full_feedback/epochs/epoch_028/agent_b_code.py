def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Target closest resource if exists; else approach opponent while staying safe
    target_res = None
    if resources:
        bestd = None
        for rx, ry in resources:
            d = abs(sx - rx) + abs(sy - ry)
            if bestd is None or d < bestd:
                bestd = d
                target_res = (rx, ry)

    # If we have a target resource, try to move towards it; else move to maximize distance from opponent while staying safe
    def toward(target):
        tx, ty = target
        best = None
        bestscore = None
        for dx, dy, nx, ny in cand:
            d = abs(nx - tx) + abs(ny - ty)
            # prefer smaller distance to target
            score = -d
            # also prefer staying away from opponent
            odist = abs(nx - ox) + abs(ny - oy)
            score = score - odist * 0.0  # keep deterministic
            if best is None or score > bestscore or (score == bestscore and (nx, ny) < (best[2], best[3])):
                best = (dx, dy, nx, ny)
                bestscore = score
        return best

    if target_res is not None:
        move = toward(target_res)
        if move:
            return [int(move[0]), int(move[1])]

    # Fallback: move away from opponent if possible, else toward center
    def distance_to_op(nx, ny):
        return abs(nx - ox) + abs(ny - oy)
    best = None
    bestdist = None
    for dx, dy, nx, ny in cand:
        d = distance_to_op(nx, ny)
        if best is None or d > bestdist or (d == bestdist and (nx, ny) < (best[2], best[3])):
            best = (dx, dy, nx, ny)
            bestdist = d
    if best:
        return [int(best[0]), int(best[1])]
    return [0, 0]