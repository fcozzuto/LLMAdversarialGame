def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def edge(x, y):
        return 1 if x == 0 or x == w - 1 or y == 0 or y == h - 1 else 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    if unclaimed:
        # Evaluate move by best target it can reach faster than opponent, plus mild center bias.
        # Deterministic: scan targets in fixed order.
        center_x, center_y = w // 2, h // 2
        best = None
        best_score = -10**18
        unclaimed_sorted = sorted(unclaimed)
        for nx, ny, dx, dy in candidates:
            d1 = manh(nx, ny, sx, sy)  # will be <=1
            my_best = -10**18
            for tx, ty in unclaimed_sorted[:20]:
                dm = manh(nx, ny, tx, ty)
                do = manh(ox, oy, tx, ty)
                # Prefer targets where we can arrive not later than opponent.
                # Also prefer closer cells and slightly safer edges (often easier to claim corridors).
                score = (do - dm) * 12 - dm + (2 if edge(tx, ty) else 0) - (manh(tx, ty, center_x, center_y) * 0.05)
                my_best = score if score > my_best else my_best
            # If opponent is adjacent, prioritize immediate capture/contestation.
            adj = 0
            if manh(nx, ny, ox, oy) <= 1:
                adj = 6
            score_move = my_best + adj - d1 * 0.01
            if best is None or score_move > best_score:
                best_score = score_move
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # If no unclaimed cells visible, stay or drift toward opponent to contest.
    best = (0, 0)
    best_score = -10**18
    for nx, ny, dx, dy in candidates:
        # Prefer moving to reduce distance to opponent.
        score = -manh(nx, ny, ox, oy) + edge(nx, ny) * 0.1
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]