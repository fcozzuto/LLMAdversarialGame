def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        best_t = None
        best_s = -10**18
        for rx, ry in resources:
            sd = king((sx, sy), (rx, ry))
            od = king((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner than opponent; tie slightly toward closer.
            s = (od - sd) * 1000 - sd
            if s > best_s:
                best_s = s
                best_t = (rx, ry)
    else:
        best_t = (int(round(cx)), int(round(cy)))

    tx, ty = best_t
    best_move = (0, 0)
    best_rank = (10**9, -10**18, -10**18)  # (dist, margin, center_bias)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = king((nx, ny), (tx, ty))
        cur_sd = king((sx, sy), (tx, ty))
        cur_od = king((ox, oy), (tx, ty))
        nd_margin = cur_od - nd
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Break ties deterministically: prioritize smaller dist; then larger margin; then higher center_bias; then move order.
        rank = (nd, -nd_margin, -center_bias)
        if rank < best_rank:
            best_rank = rank
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]