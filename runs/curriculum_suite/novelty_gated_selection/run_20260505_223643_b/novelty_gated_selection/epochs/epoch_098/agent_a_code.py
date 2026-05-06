def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Deterministic flee/approach: move to increase distance from opponent if close, else drift to center-ish
        target_x = w // 2
        target_y = h // 2
        want_opp_dist = 1 if cheb(sx, sy, ox, oy) <= 2 else 0
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            dopp = cheb(nx, ny, ox, oy)
            dc = cheb(nx, ny, target_x, target_y)
            v = (dopp if want_opp_dist else -dc)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Evaluate candidate moves by best achievable resource advantage from the next position
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        base = -cheb(nx, ny, ox, oy) * 0.02  # small pressure: stay away while moving
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; break ties by closeness and some directional bias
            v = (do - ds) * 10.0 - ds * 0.5
            if (rx + ry) % 2 == (sx + sy) % 2:
                v += 0.1
            if nx > ox:
                v += 0.05
            if v > local_best:
                local_best = v
        vmove = base + local_best
        if vmove > best_val:
            best_val = vmove
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]