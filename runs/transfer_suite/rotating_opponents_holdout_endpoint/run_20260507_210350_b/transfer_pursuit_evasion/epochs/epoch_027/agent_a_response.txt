def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_penalty(x, y):
        # Prefer staying away from obstacles; stronger when adjacent.
        p = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10**6
            if d == 1:
                p += 50
            elif d == 2:
                p += 12
            elif d == 3:
                p += 4
        return p

    # If being chased, also bias toward "edge/corner" to reduce opponent ability in zigzags.
    def edge_bias(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_val = None
    # Deterministic tie-break: use fixed order of moves.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        p = obs_penalty(nx, ny)
        if p >= 10**6:
            continue
        # Score-like objective: evader maximize (distance) and minimize obstacle penalty; pursuer opposite.
        if is_evader:
            val = (d * 100) + (edge_bias(nx, ny) * -1) - p
        else:
            val = (-d * 100) + (edge_bias(nx, ny) * 0) - p
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]