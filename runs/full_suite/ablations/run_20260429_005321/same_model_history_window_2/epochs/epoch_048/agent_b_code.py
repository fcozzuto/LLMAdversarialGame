def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick a target that favors us relative to the opponent.
    best_tx, best_ty = resources[0]
    best_adv = -10**18
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer targets we can reach sooner; break ties by keeping closer.
        adv = (opd - myd) * 100 - myd
        if adv > best_adv:
            best_adv = adv
            best_tx, best_ty = tx, ty

    # Move that maximizes immediate advantage while also reducing distance to the target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, best_tx, best_ty)
        opd = cheb(ox, oy, best_tx, best_ty)
        # Small penalty if we move into opponent's neighborhood.
        opp_near = cheb(nx, ny, ox, oy)
        opp_pen = 0 if opp_near > 2 else (3 - opp_near) * 2
        # Prefer stepping closer to the chosen target; also keep relative advantage high.
        score = (opd - myd) * 100 - myd - opp_pen
        # Deterministic tie-break: fixed order from moves list.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]