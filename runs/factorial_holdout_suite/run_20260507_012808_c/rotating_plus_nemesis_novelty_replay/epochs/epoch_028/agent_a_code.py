def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # last resort: try to move toward opponent-less corner avoiding obstacles
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy) + 0.01 * (abs(cx - ox) + abs(cy - oy))
            if best is None or d < best[0]:
                best = (d, cx, cy)
        if best is None:
            return [0, 0]
        cx, cy = best[1], best[2]
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Counter "sweep_rows": prefer resources that opponent is farther from, while still reachable.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        my = (nx, ny)
        # Choose the resource maximizing "I arrive earlier than opponent" with a strong preference.
        best_target_score = None
        nearest_my = None
        nearest_opp = None
        for tx, ty in resources:
            t = (tx, ty)
            dm = man(my, t)
            do = man((ox, oy), t)
            # If we're already on it, win immediately.
            if dm == 0:
                margin = 9999
            else:
                margin = do - dm  # positive means we are closer than opponent
            # Additional bias: avoid targets in opponent-favored rows/cols by penalizing closeness to opponent.
            target_score = 10.0 * margin - 0.2 * dm - 0.05 * do
            if best_target_score is None or target_score > best_target_score:
                best_target_score = target_score
            d2 = man(my, t)
            if nearest_my is None or d2 < nearest_my:
                nearest_my = d2
                nearest_opp = man((ox, oy), t)

        # Second-level: among equal best-target decisions, prefer moves that reduce our distance.
        penalty_stay = 0.01 if (dx == 0 and dy == 0) else 0.0
        total = best_target_score - 0.05 * (nearest_my if nearest_my is not None else 0) - penalty_stay

        if best_score is None or total > best_score:
            best_score = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]