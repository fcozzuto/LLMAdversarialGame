def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        scored = []
        for x, y in resources:
            md = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer resources I can reach first; discourage contesting likely wins by opponent.
            score = (md - od * 0.85, md, x, y)
            scored.append((score, (x, y)))
        scored.sort(key=lambda t: t[0])
        tx, ty = scored[0][1]
    else:
        # No visible resources: move to a deterministic "good" waypoint based on opponent side.
        cx, cy = w // 2, h // 2
        # If opponent is closer to center, bias away; otherwise toward center.
        if cheb(ox, oy, cx, cy) < cheb(sx, sy, cx, cy):
            tx, ty = (cx - 1, cy + 1) if valid(cx - 1, cy + 1) else (cx, cy)
        else:
            tx, ty = (cx, cy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Primary: reduce distance to target. Secondary: avoid giving opponent too-good progress.
        d_me = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Also discourage stepping too close to opponent when not improving target distance.
        d_op = cheb(nx, ny, ox, oy)
        key = (d_me, -d_op, -d_opp, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]