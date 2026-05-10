def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        return [0, 0]

    dirs = [-1, 0, 1]
    moves = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Deterministic tie-break: sort resources first
    res_list = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h:
            res_list.append((rx, ry))
    res_list.sort()

    # Choose the move that minimizes our distance advantage gap vs opponent over all resources
    best_move = (0, 0)
    best_score = None  # lower is better
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Compute best target for this candidate deterministically
        cand_best = None  # higher is better for our advantage; use stable tie-break
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: negative means opponent closer; we want max advantage (closest to resource relative to opponent)
            adv = (do - ds)
            # Deterministic tie-break: prefer smaller ds if adv equal, then smaller coords
            key = (adv, -ds, -rx, -ry)
            if cand_best is None or key > cand_best[0]:
                cand_best = (key, rx, ry, ds, do)
        # Overall: we want maximum advantage; if equal, prefer smaller distance to chosen resource
        key_move = (cand_best[0][0], -cand_best[0][1], cand_best[1], cand_best[2])
        # Convert to "lower is better" scoring for simplicity
        score = (-key_move[0], key_move[1], key_move[2], key_move[3])
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]