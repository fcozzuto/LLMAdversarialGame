def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # fall back: move to increase distance from opponent
        best = (0, 0)
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # pick a contested resource where we are not farther than the opponent
    best_res = resources[0]
    best_pair = None  # (self_time - opp_time, self_time)
    for rx, ry in resources:
        ts = cheb(sx, sy, rx, ry)
        to = cheb(ox, oy, rx, ry)
        pair = (ts - to, ts)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best_res = [rx, ry]

    tx, ty = best_res
    # one-step lookahead: prefer moving closer to target and farther to opponent's ability
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_gain = -cheb(nx, ny, tx, ty)
        opp_reach = cheb(ox, oy, tx, ty)
        # approximate opponent denial: if opponent can already reach sooner, reduce priority
        bias = 0.0
        if cheb(sx, sy, tx, ty) > cheb(ox, oy, tx, ty):
            bias = -1.5
        # slight preference to move toward contested region (not just target)
        nearest = 10**9
        for rx, ry in resources:
            t = cheb(nx, ny, rx, ry)
            if t < nearest:
                nearest = t
        v = self_gain + 0.7 * opp_reach + bias - 0.08 * nearest
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]