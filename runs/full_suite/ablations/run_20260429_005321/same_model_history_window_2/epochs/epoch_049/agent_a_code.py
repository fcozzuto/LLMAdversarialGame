def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Primary: pick best resource based on advantage (my dist vs opponent dist).
    # Secondary: avoid getting blocked and slightly prefer moving toward it.
    best_tx, best_ty = resources[0]
    best_adv = None
    # Deterministic tie-break: sort by coords.
    resources_sorted = sorted(resources)
    for tx, ty in resources_sorted:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = md - od  # smaller is better (we are closer or opponent farther)
        if best_adv is None or adv < best_adv:
            best_adv = adv
            best_tx, best_ty = tx, ty

    target = (best_tx, best_ty)

    # If resources are far behind, also consider stepping toward center to keep tempo.
    cx, cy = w // 2, h // 2
    use_center = (cheb(sx, sy, best_tx, best_ty) > 6 and cheb(ox, oy, best_tx, best_ty) > 6)

    # Also add a "blocking" bias: if we can move to reduce opponent's reach to target, do so.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_me = cheb(nx, ny, target[0], target[1])
        dist_opp = cheb(ox, oy, target[0], target[1])
        # Evaluate step: prefer smaller my dist, penalize giving opponent advantage.
        score = dist_me + 0.25 * (dist_me - (dist_opp))  # dist_me dominates
        if use_center:
            score += 0.15 * cheb(nx, ny, cx, cy)

        # Avoid stepping adjacent to many obstacles (local trap).
        trap = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx2, ty2 = nx + adx, ny + ady
                if 0 <= tx2 < w and 0 <= ty2 < h and (tx2, ty2) in obstacles:
                    trap += 1
        score += 0.05 * trap

        # Deterministic tie-break: prefer staying if equally bad? We'll use lexicographic move.
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]