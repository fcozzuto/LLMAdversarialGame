def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score: prioritize moves that make us relatively closer than opponent to a contested resource.
        # Add a small term to break ties towards nearer resources for us.
        local_best = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            val = (d_me - d_op, d_me)  # lexicographic: minimize advantage for opponent, then our distance
            if local_best is None or val < local_best:
                local_best = val

        if local_best is None:
            continue

        # Convert tuple into comparable scalar with deterministic tie-breaking.
        score = local_best[0] * 1000 + local_best[1]
        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]