def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def obst_adj(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    # Pick a target resource that we can reach earlier than opponent, with obstacle safety.
    best = None
    best_val = -10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Favor resources where we have a speed/turn advantage; break ties by safety.
        val = (od - sd) * 10 - sd
        val -= obst_adj(rx, ry) * 2
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            # Move that reduces distance; keep away from obstacles; tie-break deterministically.
            score = -d * 5 - obst_adj(nx, ny) * 2 - (abs(dx) + abs(dy)) * 0.01
            # Deterministic tie-break: prefer smaller |dx| then smaller |dy| then lexicographic.
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move