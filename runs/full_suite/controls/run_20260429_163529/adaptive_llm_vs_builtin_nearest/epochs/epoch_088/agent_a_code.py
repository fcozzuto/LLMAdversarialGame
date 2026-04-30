def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**9

    opp_turn_bias = 1 if (observation.get("turn_index", 0) % 2 == 0) else -1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Evaluate this move by the best resource to "secure" (opp_d - our_d, with slight tie-breaks)
        move_best = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            val = (opp_d - our_d) * 10 - our_d
            # Small deterministic tie-break: prefer resources more "advanced" toward top-right quadrant based on turn parity
            adv = (rx + (w - 1 - ry))
            val += (adv % 5) * 0.01 + opp_turn_bias * (cheb(ox, oy, rx, ry) % 3) * 0.001
            if val > move_best:
                move_best = val
        # Prefer moves that don't move us away from the globally best resource by our own distance
        if move_best > best_val:
            best_val = move_best
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best