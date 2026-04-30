def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = -10**9
    rr = int(observation.get("remaining_resource_count", len(resources)) or 0)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 10 - sd + (1 if sd <= od else -sd * 0.1) + (0.01 * rr)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    best_move = [0, 0]
    best_score = -10**18

    # Tie-break deterministically: prefer moves in this order
    # (-1,-1)->...->(1,1) by list order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            score = -10**12
        else:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Goal: reduce own distance, and if possible widen lead over opponent.
            score = (-myd * 10) + (opd - myd) * 3
            # Small repulsion from getting too close to opponent (avoid contest unless leading)
            score += -1.0 * cheb(nx, ny, ox, oy) * (0.2 if cheb(sx, sy, tx, ty) <= cheb(ox, oy, tx, ty) else 0.05)
            # Encourage direct approach
            score += -(abs(nx - tx) + abs(ny - ty)) * 0.01
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move