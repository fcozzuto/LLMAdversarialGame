def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if resources:
        best = None
        best_key = None
        for x, y in resources:
            dS = cheb(sx, sy, x, y)
            dO = cheb(ox, oy, x, y)
            key = (dS, -dO, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        bestm = (0, 0)
        bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            k = (cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy), dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # No resources: move away from opponent if possible; otherwise toward center-ish deterministically.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        k = (-cheb(nx, ny, ox, oy), dx, dy)
        if bestk is None or k < bestk:
            bestk = k
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]