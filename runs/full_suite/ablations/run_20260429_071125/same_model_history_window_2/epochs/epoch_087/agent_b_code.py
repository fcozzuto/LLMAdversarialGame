def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # Prefer moving toward center while staying away from opponent slightly
            score = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) + 0.15 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0] or (score == best[0] and (nx, ny) < best[1]):
                best = (score, (nx, ny))
        return [best[1][0] - sx, best[1][1] - sy] if best else [0, 0]

    # Choose one move by maximizing a deterministic "win-the-next-target" gain.
    # Gain prefers targets we are closer to than opponent, otherwise blocks nearer targets.
    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Deterministically pick the best target for this next step.
        local_best = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)

            # If opponent is closer now, we try to reduce their advantage.
            # If we are closer, we push hard to secure.
            gain = (do - ds)

            # Penalize slow approach; reward advantage.
            score = gain * 8.0 - ds * 1.2

            # Mild preference for targets that are not "behind" opponent relative to their move direction.
            # (approximate by discouraging moving toward opponent unless it also shortens target distance)
            score += 0.15 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))

            if local_best is None or score > local_best[0] or (score == local_best[0] and (tx, ty) < local_best[1]):
                local_best = (score, (tx, ty))

        # Prefer staying away from immediate capture races by maximizing local_best score.
        final_score = local_best[0]
        if best_move is None or final_score > best_score or (final_score == best_score and (nx, ny) < best_move):
            best_score = final_score
            best_move = (nx, ny)

    if best_move is None:
        return [0, 0]
    return [best_move[0] - sx, best_move[1] - sy]