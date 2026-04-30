def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = (-1, 0, 1)
    moves = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = ds - do  # smaller is better for us; negative means we're closer
            key = (adv, ds, abs(rx - cx) + abs(ry - cy), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = cx, cy

    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_t = cheb(sx, sy, tx, ty)
        prog = d_from_t - d_to_t  # positive if closer
        d_op = cheb(nx, ny, ox, oy)
        opp_term = d_op  # prefer farther from opponent
        # small preference to keep moving (avoid dithering) and toward center when tied
        center_term = -(abs(nx - cx) + abs(ny - cy))
        score = (prog * 1000) + (opp_term * 10) + center_term
        tie = 0
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tiebreaker: lexicographic by dx,dy preferring diagonals (more progress)
            if tie == 0:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]