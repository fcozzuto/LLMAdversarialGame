def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if w <= 0 or h <= 0:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        # If stepping onto a resource, strongly favor.
        step_resource = 0
        if any((rx, ry) == (nx, ny) for rx, ry in resources if (rx, ry) not in obstacles):
            step_resource = 10**6

        # Score moves by best "capture advantage" over all resources.
        # Advantage = (opp_distance - self_distance), prefer positive and then closeness.
        best_adv = -10**9
        best_close = 10**9
        best_opp = 10**9

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv or (adv == best_adv and d_self < best_close) or (adv == best_adv and d_self == best_close and d_opp < best_opp):
                best_adv = adv
                best_close = d_self
                best_opp = d_opp

        # Also count how many resources we are "closer to" than opponent (tie -> slight penalty).
        closer = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self < d_opp:
                closer += 1
            elif d_self == d_opp:
                closer -= 1

        # Deterministic tie-break: prefer moving toward center, then lexicographically.
        center_bias = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01
        val = step_resource + best_adv * 1000 + closer * 10 - best_close + center_bias

        if val > best_val or (val == best_val and (mdx, mdy) < best):
            best_val = val
            best = (mdx, mdy)

    return [best[0], best[1]]