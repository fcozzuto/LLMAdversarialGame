def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Choose move that maximizes lead on the best reachable resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Evaluate against best resource for us after this move.
        best_for_move = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Strongly prefer securing a resource where we gain a lead.
            # Small penalty for longer personal distance to keep progress.
            lead = d_opp - d_me
            v = lead * 1000 - d_me
            # Add a slight preference to move toward center-ish to reduce being trapped by denier.
            center_bias = -((7 if (nx < 4) else 0) + (7 if (ny < 4) else 0)) * 0.001
            v += center_bias
            if v > best_for_move:
                best_for_move = v
        # Also lightly discourage moves that get closer to opponent position (denial counterplay).
        sep = cheb(nx, ny, ox, oy)
        total = best_for_move + sep * 0.01
        if total > best_val:
            best_val, best_move = total, [dx, dy]
    return best_move