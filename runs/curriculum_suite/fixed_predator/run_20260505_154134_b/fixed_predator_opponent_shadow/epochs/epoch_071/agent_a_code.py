def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def val_from(x, y, rx, ry):
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        return (od - sd, -sd, -rx, -ry)

    if not resources:
        return [0, 0]

    # Choose a small deterministic candidate set of targets
    res_sorted = sorted(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]) - cheb(sx, sy, r[0], r[1]), cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    targets = res_sorted[:4] if len(res_sorted) > 4 else res_sorted

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
                continue
            moves.append((dx, dy))
    best_move = (0, 0)
    best_score = None

    # 2-ply local lookahead: move once, then move toward the best target with an obstacle-aware greedy step
    for dx0, dy0 in moves:
        x1, y1 = sx + dx0, sy + dy0
        if not inb(x1, y1) or (x1, y1) in obs:
            x1, y1 = sx, sy

        # simulate second step
        best_second = (x1, y1)
        best_second_score = None
        for rx, ry in targets:
            # greedy second step among 9 options
            best_step = (x1, y1)
            best_step_key = None
            for dx1, dy1 in moves:
                x2, y2 = x1 + dx1, y1 + dy1
                if not inb(x2, y2) or (x2, y2) in obs:
                    x2, y2 = x1, y1
                key = (cheb(x2, y2, rx, ry), abs(x2 - rx) + abs(y2 - ry), x2, y2)
                if best_step_key is None or key < best_step_key:
                    best_step_key = key
                    best_step = (x2, y2)
            x2, y2 = best_step
            score_key = val_from(x2, y2, rx, ry)
            if best_second_score is None or score_key > best_second_score or (score_key == best_second_score and (x2, y2) < best_second):
                best_second_score = score_key
                best_second = (x2, y2)

        final_score = best_second_score
        if best_score is None or final_score > best_score:
            best_score = final_score
            best_move = (dx0, dy0)

    # Ensure returned move is within allowed deltas
    return [int(best_move[0]), int(best_move[1])]