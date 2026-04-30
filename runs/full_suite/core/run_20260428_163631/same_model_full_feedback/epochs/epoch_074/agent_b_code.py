def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move to reduce distance to opponent's corner-ish: towards center to stay flexible
        tx, ty = (w // 2, h // 2)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick best target deterministically: maximize (opp_dist - our_dist), then prefer closer target
    best_target = None
    best_score = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - du, -du, -abs(rx - ox) - abs(ry - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    # Choose move that best improves our standing on that target, while not letting opponent close too fast
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Encourage faster capture, discourage moving into equal/worse contest
        val = (opp_d - my_d) * 1000 - my_d
        # Slightly prefer moves that go toward target and avoid increasing distance to all resources
        val += (cheb(sx, sy, rx, ry) - my_d) * 10
        # Tie-break: prefer smaller dx,dy magnitude then toward not moving away from center
        val += - (abs(dx) + abs(dy)) * 0.1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move