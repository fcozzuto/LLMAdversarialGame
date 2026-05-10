def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_valid(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return sx, sy
        if (nx, ny) in obs:
            return sx, sy
        return nx, ny

    # Evaluate each move by the best "counter-resource" for us after the move.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = clamp_valid(sx + dx, sy + dy)
        # Choose target that maximizes our advantage over opponent, then tie-break by closeness.
        best_t_val = None
        best_t_dist = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # higher => opponent slower than us
            # Prefer immediate capture risk: encourage small ds; penalize giving opponent near-capture targets.
            val = lead * 10.0 - ds - max(0, 2 - lead) * 3.0
            if best_t_val is None or val > best_t_val or (val == best_t_val and ds < best_t_dist):
                best_t_val = val
                best_t_dist = ds

        # Secondary objective: if two moves target similarly, pick the one that reduces our distance to its chosen target.
        # This avoids getting stuck oscillating.
        if best_val is None or best_t_val > best_val:
            best_val = best_t_val
            best_move = (dx, dy)
        elif best_t_val == best_val:
            # Deterministic tie-break: smallest (|dx|+|dy|), then lexicographic
            cur_step = abs(best_move[0]) + abs(best_move[1])
            new_step = abs(dx) + abs(dy)
            if new_step < cur_step or (new_step == cur_step and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]