def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # If no resources, drift toward the center to avoid being trapped
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    # Evaluate each move by how much it improves our advantage to the best contested resource.
    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer picking a resource we are closer to than the opponent, but also reduce our absolute distance.
        # Use a small tie-break toward lexicographically smaller move for determinism.
        cur_best = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # advantage: larger is better. Also slightly penalize if ds is large.
            val = (do - ds) * 100 - ds
            # Bonus if resource is adjacent (likely to be taken soon).
            if ds == 0:
                val += 100000
            elif ds == 1:
                val += 500
            if cur_best is None or val > cur_best:
                cur_best = val
        # Secondary tie-break: closest resource after move
        mind = min(cheb(nx, ny, tx, ty) for tx, ty in resources)
        if best_val is None or cur_best > best_val or (cur_best == best_val and mind < cheb(sx, sy, sx, sy) + mind * 0 + mind) or (cur_best == best_val and mind == min(cheb(sx + best_move[0], sy + best_move[1], tx, ty) for tx, ty in resources) and (dx, dy) < best_move):
            best_val = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]