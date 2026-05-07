def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry):
                valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in valid_resources:
            if nx == rx and ny == ry:
                s_steps = 0
                o_steps = cheb(ox, oy, rx, ry)
            else:
                s_steps = cheb(nx, ny, rx, ry)
                o_steps = cheb(ox, oy, rx, ry)

            lead = o_steps - s_steps  # positive means we are closer
            urgency = -s_steps
            # If opponent is already at/near, strongly prefer resources where we have a lead
            value = lead * 10 + urgency
            if lead <= 0:
                value -= (0 if lead == 0 else 2 * (-lead))
            if value > local_best:
                local_best = value

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]