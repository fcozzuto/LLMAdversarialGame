def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not res:
        dx = 0
        if ox < sx:
            dx = -1
        elif ox > sx:
            dx = 1
        dy = 0
        if oy < sy:
            dy = -1
        elif oy > sy:
            dy = 1
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = None

    opp_pos = (ox, oy)
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_target = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(opp_pos[0], opp_pos[1], rx, ry)
            # Prefer resources that we can reach sooner; if opponent is at least as close, penalize.
            if do <= ds:
                v = ds + 0.6 * (ds - do + 1)
            else:
                v = ds
            if best_target is None or v < best_target:
                best_target = v
        if best_target is None:
            continue

        # Slightly prefer moves that reduce distance to the currently best target overall.
        # Deterministic tie-break: choose lexicographically smaller move in score ties.
        val = best_target
        if best_val is None or val < best_val or (val == best_val and (mx, my) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [mx, my]

    # If all candidate moves were blocked, stay.
    if best_val is None:
        return [0, 0]
    return best_move