def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    if w <= 0 or h <= 0:
        return [0, 0]

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None

    if resources:
        # Prefer a resource we are closer to than opponent; otherwise fall back to our nearest.
        best = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            if do <= ds:
                continue
            key = (ds - do, ds, rx, ry)
            if best is None or key < best:
                best = key
                best_target = (rx, ry)
        if best_target is None:
            best = None
            for rx, ry in resources:
                key = (md(sx, sy, rx, ry), rx, ry)
                if best is None or key < best:
                    best = key
                    best_target = (rx, ry)

    tx, ty = (best_target if best_target is not None else (sx, sy))
    if best_target is None:
        # No resources: move to reduce distance to opponent deterministically, avoiding obstacles.
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Score: prioritize moving closer to target; also prefer moves that keep/restore advantage over opponent.
        ds = md(nx, ny, tx, ty)
        dn = md(ox, oy, tx, ty)
        opp_adv = ds - dn
        score = (opp_adv, ds, -dx, -dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]