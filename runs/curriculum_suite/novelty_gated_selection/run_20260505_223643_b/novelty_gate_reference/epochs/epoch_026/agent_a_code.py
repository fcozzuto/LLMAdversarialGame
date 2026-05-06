def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**18
        if not inb(nx, ny):
            return -10**18
        best_race = -10**18
        pick_r = None
        total = 0.0

        # Resource-denial interception: target resources where opponent is closer now,
        # and choose moves that flip who is closer after the move.
        for rx, ry in resources:
            ds_now = cheb(sx, sy, rx, ry)
            do_now = cheb(ox, oy, rx, ry)
            ds_next = cheb(nx, ny, rx, ry)
            do_next = cheb(ox, oy, rx, ry)
            if do_now <= ds_now:
                gain = (do_next - ds_next)  # positive means we are closer after move
                # Penalize letting opponent retain an advantage
                total += (gain * 120.0) - (ds_next * 2.5) - (do_next * 0.5)
                if gain > best_race:
                    best_race = gain
                    pick_r = (rx, ry)

        # If no contested resources, still prefer moving toward the resource that is closest to us
        if pick_r is None and resources:
            # Favor the nearest resource, but keep away from cells too close to opponent when tied.
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                total = max(total, (-ds * 4.0) + (do - ds) * 0.5 + (rx + ry) * 1e-3)

        # Mild anti-collision / denial: avoid getting closer to opponent unless we gain in races
        total -= cheb(nx, ny, ox, oy) * 0.2
        return total

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = score_move(nx, ny)
        # Deterministic tie-break by move order in 'moves'
        if v > best_val:
            best_val = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]