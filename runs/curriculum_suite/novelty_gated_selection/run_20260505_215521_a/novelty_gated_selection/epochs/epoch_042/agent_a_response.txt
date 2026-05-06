def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Predict opponent next position using deterministic "go to nearest resource" policy.
    nearest = resources[0]
    bestd = man(ox, oy, nearest[0], nearest[1])
    for rx, ry in resources[1:]:
        d = man(ox, oy, rx, ry)
        if d < bestd:
            bestd, nearest = d, (rx, ry)
    tx, ty = nearest
    podx = 0 if tx == ox else (1 if tx > ox else -1)
    pody = 0 if ty == oy else (1 if ty > oy else -1)
    pred_ox, pred_oy = ox + podx, oy + pody
    if not inb(pred_ox, pred_oy) or (pred_ox, pred_oy) in obst:
        pred_ox, pred_oy = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # Small resource pressure to avoid pure chasing into corners.
    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        chase = -man(nx, ny, pred_ox, pred_oy)  # interceptor: get close to where opponent will be
        # resource tie-break: prefer states where we're closer than opponent
        res_adv = -10**18
        for rx, ry in resources:
            ourd = man(nx, ny, rx, ry)
            opd = man(pred_ox, pred_oy, rx, ry)
            score = (opd - ourd) * 10 - ourd
            if score > res_adv:
                res_adv = score
        score = chase * 100 + res_adv
        if score > best_score:
            best_score, best = score, (dx, dy)

    return [int(best[0]), int(best[1])]