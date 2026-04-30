def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**6
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in occ:
                    pen += 25 if (dx == 0 or dy == 0) else 17
        return pen

    def step_reward(nx, ny):
        if not inb(nx, ny):
            return -10**9
        if (nx, ny) in occ:
            return -10**9
        best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; also encourage general closeness.
            advantage = do - ds
            val = advantage * 100 - ds
            if (nx, ny) == (rx, ry):
                val += 100000  # immediate pickup preference
            # If opponent likely contesting, increase its weight.
            if do <= 2 and ds <= 2:
                val += 800
            if val > best:
                best = val
        if best == -10**18:
            best = -cheb(nx, ny, ox, oy)  # fallback: reduce distance to opponent to contest
        return best - near_obstacle_pen(nx, ny)

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = step_reward(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]