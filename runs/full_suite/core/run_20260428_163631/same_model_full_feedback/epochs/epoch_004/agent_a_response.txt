def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, head deterministically toward opponent (pursuit).
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny):
            return [dx, dy]
        # fallback: smallest safe move that reduces cheb distance to opponent
        best = (10**9, 0, 0)
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not safe(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            if d < best[0] or (d == best[0] and (ddx, ddy) < (best[1], best[2])):
                best = (d, ddx, ddy)
        return [best[1], best[2]]

    # Otherwise: choose a move that maximizes "steal pressure" on the best resource for us.
    best_score = None
    best_move = (0, 0)
    # Deterministic ordering for tie breaks
    deltas_sorted = sorted(deltas)

    for ddx, ddy in deltas_sorted:
        nx, ny = sx + ddx, sy + ddy
        if not safe(nx, ny):
            continue

        # Pick the resource that gives maximum steal pressure from our hypothetical next position.
        # Pressure: (opponent distance to resource) - (our distance to resource).
        local_best = None
        local_best_res = None
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            od = cheb(ox, oy, rx, ry)
            sd = cheb(nx, ny, rx, ry)
            pressure = od - sd
            # Tie-break: prefer higher pressure, then smaller our distance, then lexicographic resource
            key = (-pressure, sd, rx, ry)
            if local_best is None or key < local_best:
                local_best = key
                local_best_res = (rx, ry, pressure, sd, od)

        rx, ry, pressure, sd, od = local_best_res
        # Secondary objective: our absolute closeness and slight preference to reduce opponent advantage
        # Score higher is better.
        score = (pressure * 1000) - sd + (1 if (nx == rx and ny == ry) else 0)

        if best_score is None or score > best_score or (score == best_score and (ddx, ddy) < best_move):
            best_score = score
            best_move = (ddx, ddy)

    return [best_move[0], best_move[1]]