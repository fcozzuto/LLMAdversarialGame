def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**9

    # If no resources, drift to board center while avoiding obstacles.
    if not resources:
        cx, cy = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = -(cheb(nx, ny, cx, cy))
                if score > best_score or (score == best_score and (dx, dy) < best_move):
                    best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]

    # Otherwise, move to improve relative advantage: (opp_dist - self_dist) to the best target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Encourage not to step into immediate resource if opponent is also close there: tie-break deterministically.
        local_best = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Large weight on relative advantage; small weight on absolute closeness to reduce dithering.
            rel = do - ds
            abs_adv = -ds
            score = rel * 100 - ds + (abs_adv // 2)
            # Prefer nearer resources when equal relative advantage.
            if score > local_best or (score == local_best and (rx, ry) < (nx, ny)):
                local_best = score

        # Small penalty if moving closer to opponent without improving target advantage.
        opp_close_pen = -cheb(nx, ny, ox, oy) // 10
        total = local_best + opp_close_pen

        if total > best_score or (total == best_score and (dx, dy) < best_move):
            best_score, best_move = total, (dx, dy)

    return [best_move[0], best_move[1]]