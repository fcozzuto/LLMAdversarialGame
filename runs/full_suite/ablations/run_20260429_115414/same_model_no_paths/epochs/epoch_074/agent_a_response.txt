def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a materially different deterministic target: maximize opponent-advantage margin,
    # but only among resources where we are not hopelessly far.
    target = None
    best_margin = -10**9
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        margin = (od - sd)  # positive means we are closer
        # If resources are sparse, avoid chasing very far targets.
        far_pen = sd if sd > 6 else 0
        score = margin * 20 - far_pen
        if score > best_margin:
            best_margin = score
            target = (tx, ty)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if target is None:
        # No visible resources: move to reduce distance to center while staying valid.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_s = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            sc = -d
            if sc > best_s:
                best_s = sc
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    tx, ty = target
    oppd = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd_new = cheb(nx, ny, tx, ty)
        adv_new = oppd - sd_new
        # Primary: maximize our advantage; Secondary: minimize our distance.
        score = adv_new * 25 - sd_new
        # Micro-avoid: if we're already equal/behind, prefer progress (lower sd).
        if adv_new <= 0:
            score -= sd_new * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]