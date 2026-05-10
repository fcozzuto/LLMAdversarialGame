def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = int(p["x"]), int(p["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = "evader" in role

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                targets.append((rx, ry))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            rx, ry = int(r["x"]), int(r["y"])
            if inb(rx, ry) and (rx, ry) not in obs:
                targets.append((rx, ry))
    if targets:
        tx, ty = min(targets, key=lambda p: cheb(sx, sy, p[0], p[1]))
    else:
        tx, ty = (ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if evader and not targets:
            # evade opponent when no resources to pursue
            v = cheb(nx, ny, ox, oy)
        else:
            # pursue resource if present, otherwise approach opponent
            v = -cheb(nx, ny, tx, ty) if not evader else cheb(nx, ny, tx, ty)
        # Prefer moves that also don't get immediately stuck near obstacles
        adj_block = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = nx + ax, ny + ay
            if not inb(xx, yy) or (xx, yy) in obs:
                adj_block += 1
        key = (adj_block, v)
        if best is None or key < best_val:
            best = [dx, dy]
            best_val = key

    if best is None:
        return [0, 0]
    return best