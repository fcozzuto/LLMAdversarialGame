def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    r += 2
        return r

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not resources:
        return [0, 0]

    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obst:
            continue

        # Evaluate move by how much closer we can get than the opponent to the best resource.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do == 0 and ds != 0:
                continue  # opponent already on resource; deprioritize
            # Prefer large advantage; break ties toward smaller ds and closer resource coordinates.
            advantage = (do - ds)
            val = advantage * 100 - ds * 3 - cheb(nx, ny, sx, sy) - risk(nx, ny) * 2
            if ds == 0:
                val += 1000
            if (rx + ry) % 2 == 0:
                val += 0.5  # deterministic tie nudges
            if val > local_best:
                local_best = val

        # Mildly encourage moves that reduce distance to the currently best resource if any.
        # (Handled implicitly by local_best, but keep deterministic tie-breaking)
        score = local_best
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best