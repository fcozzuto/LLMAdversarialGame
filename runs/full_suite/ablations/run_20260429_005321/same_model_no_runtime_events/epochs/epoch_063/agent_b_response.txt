def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_opp = max(abs(nx - ox), abs(ny - oy))
            score = d_opp
            key = (score, -dx, -dy)
            if best is None or key > best:
                best = key
                best_move = [int(dx), int(dy)]
        return best_move

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose overall target deterministically: closest resource by Chebyshev, tie by coords
    target = None
    best_td = None
    for rx, ry in resources:
        td = cheb(sx, sy, rx, ry)
        if best_td is None or td < best_td or (td == best_td and (rx, ry) < target):
            best_td = td
            target = (rx, ry)

    tx, ty = target
    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_res = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer decreasing resource distance while also increasing distance to opponent.
        # Small tie-breakers ensure determinism.
        score = (-d_res) * 1000 + d_opp
        key = (score, -d_res, -d_opp, -dx, -dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [int(dx), int(dy)]
    return best_move