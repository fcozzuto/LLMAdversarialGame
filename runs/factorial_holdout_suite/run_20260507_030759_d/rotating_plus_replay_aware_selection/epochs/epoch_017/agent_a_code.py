def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_dx = 0
    best_dy = 0
    best_score = -10**18

    # Bias toward progressing to the "opposite" side (works with opposite-corner starts)
    # and toward collecting sooner.
    progress_bias = 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate next cell by best resource for us vs opponent
        local_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            if ds == 0 and (nx, ny) == (rx, ry):
                local = 10**12
            else:
                do = man(ox, oy, rx, ry)
                # Prefer where we gain relative to opponent; break ties by closer to resource.
                local = (do - ds) * 500 - ds * 7
            if local > local_best:
                local_best = local

        # Small deterministic tie-break: prefer increased progress (x+y), then prefer toward right-up
        tie = (nx + ny) * progress_bias + (nx - ny) * 0.1
        score = local_best + tie
        if score > best_score:
            best_score = score
            best_dx = dx
            best_dy = dy

    return [int(best_dx), int(best_dy)]