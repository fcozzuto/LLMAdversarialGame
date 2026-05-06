def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def best_for(px, py):
        if not resources:
            return man(px, py, cx, cy), (cx, cy)
        best_d = None
        best_r = resources[0]
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_r):
                best_d, best_r = d, (rx, ry)
        return best_d, best_r

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = man(nx, ny, cx, cy)
                if best is None or d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    opp_best_d, opp_target = best_for(ox, oy)

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_d, self_target = best_for(nx, ny)
        # Main objective: win resource race; secondary: improve distance after taking it.
        # Bonus if we align with opponent's nearest target (direct contention).
        contention = 0
        if self_target == opp_target:
            contention = 2
        # Encourage progress even if tied: slightly prefer smaller self_d.
        score = (opp_best_d - self_d) + contention - self_d * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]