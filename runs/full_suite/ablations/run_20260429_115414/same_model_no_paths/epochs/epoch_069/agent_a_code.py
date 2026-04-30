def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def block_adj(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if ddx == 0:
                pass
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_target = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources where we are closer; otherwise, pick the least contested-ish.
        key = (-(sd - od), -sd, tx + ty, tx, ty)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    if best_target is None:
        tx, ty = ox, oy  # fallback
    else:
        tx, ty = best_target

    # Move choice: minimize (our distance to target) with obstacle/edge pressure and slight opponent-blocking.
    best_move = (0, 0)
    best_score = None
    # Deterministic order: prefer progress (dx sign) via tie-breaks in key.
    order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_ours = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)  # fixed but keeps intent consistent
        # Small penalty if we would get more adjacent to obstacles; small incentive to reduce opponent advantage.
        score = (d_ours, block_adj(nx, ny), cheb(nx, ny, ox, oy), (d_ours - d_opp), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]