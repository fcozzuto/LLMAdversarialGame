def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w // 2), (h // 2)
        best, bestd = (0, 0), -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = -cheb(nx, ny, tx, ty) + (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))
            if score > bestd:
                bestd, best = score, [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moves that secure a resource sooner than the opponent, while still moving toward high-value targets.
        move_score = 0
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Win-taking: bigger when we are closer (or tie and we are nearer after move).
            take = (opp_d - our_d)
            # Encourage actually progressing: smaller our_d is better.
            prog = -our_d
            # Mild center bias to avoid corner-stalling late game.
            cb = -abs(rx - (w // 2)) - abs(ry - (h // 2))
            move_score += (take * 10 + prog * 2 + cb * 0.2)
        # Avoid moving away when standing on a resource is possible (engine may keep if invalid, but we handle by valid).
        if (sx, sy) in resources:
            move_score += 1000 if (nx, ny) == (sx, sy) else -5
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move