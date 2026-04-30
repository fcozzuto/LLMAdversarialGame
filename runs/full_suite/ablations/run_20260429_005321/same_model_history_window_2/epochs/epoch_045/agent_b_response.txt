def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            score = cheb(nx, ny, ox, oy)  # maximize distance if no resources
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] else [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_opp_gap = cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)

        # Evaluate best "advantage" resource after the move
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; discourage letting them be closer
            advantage = od - sd
            # Also prefer minimizing our distance once aiming
            target_score = 2.5 * advantage - 0.15 * sd + 0.08 * my_opp_gap
            if target_score > local_best:
                local_best = target_score

        # If no clear advantage exists, fall back to safety + approach the closest resource
        closest_sd = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        fallback = 1.2 * cheb(nx, ny, ox, oy) - 0.25 * closest_sd
        score = local_best if local_best > 0 else 0.7 * local_best + 0.3 * fallback

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]