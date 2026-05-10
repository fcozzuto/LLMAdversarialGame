def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation.get("opponent_position", (ax, ay))
    obstacles = observation.get("obstacles") or []
    obs = set(obstacles)

    resources = observation.get("resources") or []
    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Core heuristic: approach opponent, collect resources, keep away from obstacles.
        dist_op = abs(nx - ox) + abs(ny - oy)

        if resources:
            dist_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            dist_res = 999999

        # Obstacle proximity penalty (local)
        prox = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if (nx + adx, ny + ady) in obs:
                    prox += 1

        # Slight preference for staying deterministic and not too random
        v = dist_op * 10 + dist_res * 2 - (1 if (nx, ny) in res_set else 0) + prox * 100 + (dx * 0 + dy * 0)
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]