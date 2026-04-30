def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue

            score = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer positions where we are closer than opponent; small tie-break for being also close to us.
                v = (opd - myd) * 100 - myd
                if v > score:
                    score = v

            # If no resource gives positive advantage, still move to reduce our best distance.
            if score <= -10**17:
                score = -sum(cheb(nx, ny, rx, ry) for rx, ry in resources)

            # Tie-break deterministically toward opponent direction
            tie = -(cheb(nx, ny, ox, oy))
            val = score * 1000 + tie
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources visible: move toward opponent to block.
        tx, ty = ox, oy
        # Prefer reducing chebyshev distance to opponent; deterministic tie-break by dx then dy order already.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            val = -cheb(nx, ny, tx, ty)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]