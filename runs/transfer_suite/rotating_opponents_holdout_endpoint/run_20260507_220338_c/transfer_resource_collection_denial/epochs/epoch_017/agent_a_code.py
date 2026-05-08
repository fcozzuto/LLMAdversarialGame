def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    best = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cur = 0
        step_gain = 0
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer collecting now or denying better than opponent.
            if nx == rx and ny == ry:
                s = 10**9
            else:
                # Higher when we are closer than opponent (od - sd positive),
                # discourage moving toward far resources.
                s = (od - sd) * 250 - sd * 2
            # Deterministic preference among equals
            s -= i * 0.01
            # Slightly bias toward shorter travel to reduce dithering
            s -= (nx + 1) * 1e-6 + (ny + 1) * 1e-6
            step_gain += s

        cur = step_gain
        if cur > best:
            best = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]