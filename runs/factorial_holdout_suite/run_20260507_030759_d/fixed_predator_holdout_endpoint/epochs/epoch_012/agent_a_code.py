def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = max(abs(tx - nx), abs(ty - ny))
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    ox, oy = observation["opponent_position"]
    def cheb(a, b, c, d):
        return max(abs(c - a), abs(d - b))

    # If we can secure a resource (strictly closer), do it; otherwise deny by moving toward the best contested one.
    best_move = None
    best_score = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: advantage over opponent from this move; Secondary: prefer closer even if still behind.
            advantage = od - sd
            secure = 1 if sd < od else 0
            s = (secure, advantage, -sd)
            if best_for_move is None or s > best_for_move:
                best_for_move = s
        # Tie-break across moves deterministically
        if best_score is None or best_for_move > best_score or (best_for_move == best_score and (dx, dy) < best_move):
            best_score = best_for_move
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]