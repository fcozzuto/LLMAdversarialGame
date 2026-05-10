def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y, tx, ty):
        ax = x - tx
        if ax < 0:
            ax = -ax
        ay = y - ty
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def manh(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx + dy

    i_am_evader = ("evader" in self_role) and ("pursuer" not in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # For evader: run to farthest corner; for pursuer: aim to reduce distance while steering to corner the evader occupies.
    if i_am_evader:
        target_corner = max(corners, key=lambda c: manh(sx, sy, c[0], c[1]))
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # If distance ties, drift toward target corner; if still tie, prefer staying away from opponent's corner region.
            tie = -manh(nx, ny, target_corner[0], target_corner[1]) - (manh(nx, ny, ox, oy) == d) * 0
            v = d * 100000 + tie
            if best is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Pursuer behavior
    opp_corner = min(corners, key=lambda c: manh(ox, oy, c[0], c[1]))
    best = None
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Primary: minimize chebyshev distance; secondary: move toward opponent's corner to constrain escape.
        tie = manh(nx, ny, opp_corner[0], opp_corner[1]) + 0.1 * manh(nx, ny, ox, oy)
        v = d * 100000 + tie
        if best is None or v < bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]