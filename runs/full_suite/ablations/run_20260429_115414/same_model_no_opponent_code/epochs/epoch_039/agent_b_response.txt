def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        dx = 0
        if ox != sx:
            dx = 1 if ox > sx else -1
        dy = 0
        if oy != sy:
            dy = 1 if oy > sy else -1
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        if valid(sx, sy):
            return [0, 0]
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if valid(sx + tx, sy + ty):
                    return [tx, ty]
        return [0, 0]

    mode = int(observation.get("turn_index", 0) or 0) % 2

    best = None
    for rx, ry in resources:
        if mode == 0:
            key = (cheb(sx, sy, rx, ry), cheb(ox, oy, rx, ry), rx, ry)
        else:
            key = (cheb(ox, oy, rx, ry), cheb(sx, sy, rx, ry), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Choose move that decreases distance to target; tie-break deterministically.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                # Secondary: reduce opponent ability to reach simultaneously (contested bias)
                contested = cheb(nx, ny, ox, oy)
                candidates.append((d, contested, dx, dy))
    candidates.sort()
    if candidates:
        return [int(candidates[0][2]), int(candidates[0][3])]
    return [0, 0]