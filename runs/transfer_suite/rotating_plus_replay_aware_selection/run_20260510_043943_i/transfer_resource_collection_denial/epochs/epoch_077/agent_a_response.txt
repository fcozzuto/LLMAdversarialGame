def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    if not resources:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        # Avoid "staying" only if we have feasible alternatives
        moved = 1 if (nx != sx or ny != sy) else 0

        # Pick best resource for this move by advantage-first
        best_for_move = None
        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            myd = dist_cheb(nx, ny, rx, ry)
            opd = dist_cheb(ox, oy, rx, ry)
            # Advantage: bigger is better; prefer lower myd for tie-break
            adv = opd - myd
            # If can't beat opponent soon, still choose the best pressure point
            # Add tiny deterministic bias to avoid ties
            bias = (rx * 31 + ry) % 7
            val = (adv, moved, -myd, bias)
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        if best_for_move is None:
            continue
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]