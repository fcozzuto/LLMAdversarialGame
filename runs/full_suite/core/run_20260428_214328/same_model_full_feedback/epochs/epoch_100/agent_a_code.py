def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_block(x, y):
        return 1 if (x, y) in obstacles else 0

    def obstacle_pressure(x, y):
        # Penalize moves that bring us near obstacles (to reduce trapping cycles)
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    # Strategy: pick move that maximizes advantage to the most "beatable" resource.
    # Advantage = opponent_dist - our_dist. Also penalize obstacle pressure.
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        local_best = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            # Prefer targets we can reach quickly; avoid those opponent also reaches instantly.
            score = (adv, -our_d, -abs(opp_d - our_d), -(cell_block(rx, ry)), 0)
            if local_best is None or score > local_best:
                local_best = score
        # obstacle pressure discourages risky corridor moves
        total = (local_best[0], local_best[1], local_best[2], -obstacle_pressure(nx, ny), -abs(nx - ox) - abs(ny - oy))
        if best_score is None or total > best_score:
            best_score = total
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]