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

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = md(nx, ny, cx, cy)
                if best is None or val < best[0]:
                    best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Evaluate each move by how much it improves relative access to resources (not just nearest).
    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Prefer resources where we're closer than opponent after this move; otherwise prefer reducing disadvantage.
        best_for_move = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Negative means we're ahead; prioritize strongly being ahead, but also reduce worst-case disadvantage.
            rel = ds - int(1.15 * do)
            # Tie-break by preferring closer resource to ensure progress.
            t = (ds, -rx, -ry)
            if best_for_move is None or rel < best_for_move[0] or (rel == best_for_move[0] and t < best_for_move[1]):
                best_for_move = (rel, t)

        # Add mild center drift to reduce oscillations and help late-game.
        center = md(nx, ny, cx, cy)
        val = best_for_move[0] * 100 + best_for_move[1][0] + center * 0.05
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]