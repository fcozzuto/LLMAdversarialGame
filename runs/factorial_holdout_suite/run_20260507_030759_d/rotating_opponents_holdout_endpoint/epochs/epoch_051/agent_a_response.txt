def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        # drift away from opponent to avoid getting blocked when no visible resources
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = abs(nx - ox) + abs(ny - oy)
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2 and isinstance(r[0], int) and isinstance(r[1], int):
            rx, ry = r[0], r[1]
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_set.add((rx, ry))
    resources = list(res_set) if res_set else resources

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Evaluate each move by best contested resource after moving one step.
    # Maximize advantage = (opp_dist - self_dist) + small preference for closer self.
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_here = (nx, ny) in res_set
        d_self = {}
        for r in resources:
            d_self[r] = (dist((nx, ny), r), dist((ox, oy), r))
        # Choose the resource that maximizes advantage; if multiple, prefer one that gives nearer self.
        best_res_val = None
        for r in resources:
            sd, od = d_self[r]
            advantage = (od - sd)
            if self_here and r == (nx, ny):
                advantage += 1000
            # If opponent is already very close, reduce willingness to chase; prefer resources with clear edge.
            contest_penalty = 0
            if od <= sd and not (self_here and r == (nx, ny)):
                contest_penalty = 2 * (sd - od + 1)
            val = advantage - contest_penalty - 0.1 * sd
            if best_res_val is None or val > best_res_val or (val == best_res_val and r < best_res):
                best_res_val = val
                best_res = r
        # Secondary tie-break: prefer moves that increase distance from opponent slightly (avoid head-to-head blocking).
        d_opp = dist((nx, ny), (ox, oy))
        final = best_res_val + 0.01 * d_opp
        if best_val is None or final > best_val or (final == best_val and (dx, dy) < best_move):
            best_val = final
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]