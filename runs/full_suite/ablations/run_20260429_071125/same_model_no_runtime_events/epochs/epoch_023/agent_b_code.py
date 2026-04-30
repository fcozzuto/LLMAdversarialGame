def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x")
                y = r.get("y")
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs_order = deltas[:]  # deterministic

    def resource_priority(rx, ry):
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If opponent is closer, heavily penalize to avoid losing contested resources
        # Slightly prefer positions that reduce opponent distance too (indirect pressure).
        risk = 0
        if od < md:
            risk = 6
        return md + risk - 0.15 * od

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            pr = resource_priority(rx, ry)
            if best is None or pr < best:
                best = pr
                target = (rx, ry)
    if target is None:
        # Default: head toward center but keep some distance from opponent
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # Prefer closer to target; if tied, prefer farther from opponent; if still tied, deterministic by order
        val = (dist_to_target, -dist_to_opp)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]