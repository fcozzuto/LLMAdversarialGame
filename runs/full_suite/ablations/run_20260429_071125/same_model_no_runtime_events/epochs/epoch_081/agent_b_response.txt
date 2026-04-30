def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If no resources, drift to maximize separation control (toward our corner away from opponent).
    if not resources:
        tx = 0 if sx > (w - 1) - sx else (w - 1)
        ty = 0 if sy > (h - 1) - sy else (h - 1)
        bx = 0 if sx == tx else (1 if sx < tx else -1)
        by = 0 if sy == ty else (1 if sy < ty else -1)
        return [int(bx), int(by)]

    resources_sorted = sorted(resources)  # deterministic tie-break

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # Choose a target deterministically: best per-move among resources via score.
        move_best = -10**18
        for rx, ry in resources_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources we can reach at least as fast; otherwise pick those that still advantage us.
            gain = (do - ds)
            # If we land on a resource, massively prefer.
            on = 1 if (nx == rx and ny == ry) else 0
            # Prefer closer targets when gain ties; and slightly prefer left/up for determinism.
            local = (on * 10**6) + (gain * 1000) - (ds * 3) - (rx + ry * w) * 0.0001
            if local > move_best:
                move_best = local
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]