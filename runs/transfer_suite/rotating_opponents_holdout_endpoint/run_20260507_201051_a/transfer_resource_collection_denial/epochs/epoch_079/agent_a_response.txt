def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = w - 1 if sx < (w - 1) // 2 else 0
        ty = h - 1 if sy < (h - 1) // 2 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        row_lock = 0
        if ry == oy:
            row_lock = 2  # avoid easy sweep-row grabs
        col_lock = 0
        if rx == ox:
            col_lock = 1
        # Prefer resources where we arrive earlier; if close, prefer farther "space" from opponent
        key = (od - sd - row_lock - col_lock, -(sd + 0.1 * (rx + ry)), (rx, ry))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    best_move = (0, 0)
    best_md = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        md = cheb(nx, ny, tx, ty)
        # Also discourage moving onto opponent's row too closely (deterministic)
        penalty = 0
        if ny == oy and cheb(nx, ny, ox, oy) <= 2:
            penalty = 1
        md_pen = md + penalty
        if best_md is None or md_pen < best_md or (md_pen == best_md and (dx, dy) < best_move):
            best_md = md_pen
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]