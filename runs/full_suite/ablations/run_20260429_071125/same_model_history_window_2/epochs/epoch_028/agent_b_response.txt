def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2
    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = kdist(sx, sy, rx, ry)
            do = kdist(ox, oy, rx, ry)
            # Strongly prefer winning races, then prefer closer, then prefer more "late" (nearer high index)
            v = (2000 if ds < do else 0) + (do - ds) * 50 - ds * 10
            v += -(rx + 2 * ry) * 0.01  # deterministic tie-break
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = cx, cy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = kdist(nx, ny, tx, ty)
        do = kdist(ox, oy, tx, ty)
        # If resource race: keep moving to reduce distance; otherwise: move closer to target/center
        v = -ds * 10 + (2000 if kdist(nx, ny, tx, ty) < do else 0)
        if not resources:
            v += -kdist(nx, ny, cx, cy) * 2
        scored.append((v, ds, abs(dx), dx, dy))
    if not scored:
        # Shouldn't happen, but return stay
        return [0, 0]
    scored.sort(reverse=True)
    _, _, _, dx, dy = scored[0]
    return [int(dx), int(dy)]