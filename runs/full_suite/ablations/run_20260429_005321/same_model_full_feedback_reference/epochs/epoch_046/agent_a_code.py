def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target deterministically
    if resources:
        best = None
        best_score = None
        for tx, ty in resources:
            ds = dist2(sx, sy, tx, ty)
            do = dist2(ox, oy, tx, ty)
            adv = do - ds  # positive means we are closer
            # prioritize capture likelihood, then closeness, then deterministic tie-break
            score = (adv, -ds, (tx + ty) * 0.0001 + (tx * 0.00001) + (ty * 0.000001))
            if best is None or score > best_score:
                best = (tx, ty)
                best_score = score
        tx, ty = best
    else:
        # No visible resources: move toward opponent but avoid obstacles
        tx = w - 1 if sx < ox else 0
        ty = h - 1 if sy < oy else 0

    # Evaluate candidate moves
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        new_ds = dist2(nx, ny, tx, ty)
        new_do = dist2(ox, oy, tx, ty)
        # Advancing target; also slightly keep distance from opponent while contesting
        adv = new_do - new_ds
        opp_d = dist2(nx, ny, ox, oy)
        val = (adv, -new_ds, opp_d)

        # deterministic tie-break on move ordering
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]