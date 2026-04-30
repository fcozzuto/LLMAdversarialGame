def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    resources = observation.get("resources") or []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dcheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        best = -10**18
        for rx, ry in resources:
            ds = dcheb(x, y, rx, ry)
            do = dcheb(ox, oy, rx, ry)
            # Material swing: prefer resources where we can get there sooner.
            key = (do - ds) * 25 - ds
            # If we can tie/edge, slightly prefer to advance toward it (deterministic contesting).
            if ds <= do:
                key += 3
            best = key if key > best else best
        if resources:
            return best
        # No resources: drift to a safe center while not letting opponent rush us.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return -dcheb(x, y, cx, cy) - 0.5 * dcheb(x, y, ox, oy)

    # Choose target implicitly via best move to a high-scoring cell.
    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: fixed move order already.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]