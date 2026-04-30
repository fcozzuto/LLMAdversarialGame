def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = 10**9
            opd = 10**9
            immediate = 0
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < myd:
                    myd = d1
                d2 = cheb(ox, oy, rx, ry)
                if d2 < opd:
                    opd = d2
                if nx == rx and ny == ry:
                    immediate = 1
            # Prefer being the closer one to the nearest resource; also race at that resource.
            score = 1000 * immediate + (-myd) * 10 + (opd - myd) * 3
            # Light preference to progress generally toward opponent side if tied.
            score += -(cheb(nx, ny, ox, oy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No visible resources: drift to center and keep some distance from opponent.
        cx, cy = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy) * 2 - cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [int(dx), int(dy)]