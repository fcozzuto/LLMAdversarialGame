def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Prefer moves that get us closer to a resource relative to the opponent.
    # If that fails, fall back to closest resource while also slightly distancing from opponent.
    best_key = None
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_gain = -10**9
        best_sd = 10**9
        best_res = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd
            if gain > best_gain or (gain == best_gain and (sd < best_sd or (sd == best_sd and (rx, ry) < best_res))):
                best_gain = gain
                best_sd = sd
                best_res = (rx, ry)

        # Extra terms to stabilize: avoid letting opponent get significantly closer right after our move.
        dist_self_opp = md(nx, ny, ox, oy)
        dist_opp_to_best = md(ox, oy, best_res[0], best_res[1]) if best_res else md(ox, oy, nx, ny)
        # Key: maximize relative advantage, then be close to chosen resource, then stay away from opponent.
        key = (best_gain, -best_sd, dist_self_opp, -(dist_opp_to_best), -(nx + ny), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]