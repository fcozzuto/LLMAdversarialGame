def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Novelty: move to maximize distance from opponent (denier-friendly, avoids chasing)
        best_move = [0, 0]
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles: 
                continue
            val = cheb(nx, ny, ox, oy)  # maximize separation
            if val > best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    # Decide targeting based on who is closer to a resource; if opponent is closer, move to deny by approaching that resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue

        # Base incentive: prevent opponent from gaining nearer distance on the most relevant resource
        move_val = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Resource priority: prefer resources where we can be competitive.
            # If opponent is closer, we still move toward them but penalize direct race vs closer resources.
            # Also slight preference for being closer to the "best deny target" (max of (od-sd)).
            gap = od - sd
            # Scale: prioritize closer resources (smaller sd/od) deterministically
            close_bias = (16 - sd) - 0.5 * (16 - od)
            # Denier flavor: positive gap is good; negative gap still can be chosen if opponent can't quickly capture.
            move_val += (gap * 3 + close_bias)

        # Tie-break: slightly keep moves that also increase overall distance from opponent (avoid mutual blocking deadlocks)
        move_val += 0.1 * cheb(nx, ny, ox, oy)

        if move_val > best_val:
            best_val, best_move = move_val, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]