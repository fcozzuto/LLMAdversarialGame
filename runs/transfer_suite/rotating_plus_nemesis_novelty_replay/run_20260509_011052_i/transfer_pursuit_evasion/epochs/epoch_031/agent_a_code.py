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
        ax = abs(x - tx)
        ay = abs(y - ty)
        return ax if ax > ay else ay

    i_am_evader = ("evader" in self_role) and ("pursuer" not in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def wall_penalty(x, y):
        # discourage stepping into tight spaces near obstacles/boundaries
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    pen += 1
                elif (nx, ny) in obstacles:
                    pen += 2
        return pen

    best = None
    bestv = -10**18 if i_am_evader else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        if i_am_evader:
            # maximize distance; bias to far corner; avoid being boxed
            v = dist * 1000 - (abs(nx - far_corner[0]) + abs(ny - far_corner[1])) - wall_penalty(nx, ny) * 3
            if v > bestv:
                bestv = v
                best = (dx, dy)
        else:
            # minimize distance; bias to reduce both coordinates; avoid obstacles
            v = dist * 1000 + abs(nx - ox) + abs(ny - oy) + wall_penalty(nx, ny) * 2
            if v < bestv:
                bestv = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]