def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles", [])
    obst = set((p[0], p[1]) for p in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        s = 0
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Herding/denial: prefer resources where we are or become relatively closer,
            # and otherwise prioritize reducing our distance when opponent is ahead.
            rel = op_d - my_d  # positive => I am closer than opponent
            if rel >= 0:
                s += (rel * 100 - my_d * 5)  # consolidate lead
            else:
                s += (-my_d * 25 + op_d * 2)  # claw back when behind

        # Small tie-break: prefer moves that bring us closer to the closest resource overall.
        base = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        s -= base

        if s > best_score:
            best_score = s
            best_move = [dx, dy]

    return best_move