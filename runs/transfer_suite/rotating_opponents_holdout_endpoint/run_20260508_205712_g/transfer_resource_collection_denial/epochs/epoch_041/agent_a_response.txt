def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    if not resources:
        # drift to maximize distance from opponent (deterministic)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = cheb(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Precompute resource positions for deterministic iteration order
    res = sorted((r[0], r[1]) for r in resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate the most "winnable" resource from the candidate position
        local_best = None
        for rx, ry in res:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; break ties by self distance.
            cand = (oppd - selfd, -selfd, -rx, -ry)
            if local_best is None or cand > local_best:
                local_best = cand
        # Add small terms: avoid moves that allow immediate opponent gain by increasing opp distance.
        opp_after = cheb(nx, ny, ox, oy)
        score = local_best[0] * 10 + (-local_best[1]) + 0.01 * opp_after
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]