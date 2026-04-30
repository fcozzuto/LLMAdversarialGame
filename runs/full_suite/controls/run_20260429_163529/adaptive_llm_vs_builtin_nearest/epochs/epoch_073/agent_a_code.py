def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            # Engine may keep agent in place, but reflect that here by evaluating from current pos
            nx, ny = sx, sy

        # Evaluate best target from this candidate next position
        move_score = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive when we are closer than opponent (good contest)
            adv = do - ds
            # Deterministic tie-break using geometry
            tie = ((rx + 3 * ry + 5 * (rx - ry)) % 11) - 5
            val = adv * 20 - ds * 2 + tie
            if val > move_score:
                move_score = val
        key = (move_score, -(abs((sx + dxm) - ox) + abs((sy + dym) - oy)))
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]