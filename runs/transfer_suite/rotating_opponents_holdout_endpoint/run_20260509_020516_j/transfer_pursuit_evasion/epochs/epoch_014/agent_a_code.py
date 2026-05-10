def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    i_am_pursuer = "pursuer" in role and "evader" not in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def score_move(nx, ny):
        # Evader: maximize pursuer distance; Pursuer: minimize pursuer distance.
        dist = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Wall-aware: prefer moves with more free neighbors.
        free = 0
        for dx2, dy2 in deltas:
            x2, y2 = nx + dx2, ny + dy2
            if inb(x2, y2) and not blocked(x2, y2):
                free += 1

        # Obstacle avoidance: slightly penalize being adjacent to obstacles.
        adj = 0
        for dx2, dy2 in deltas:
            x2, y2 = nx + dx2, ny + dy2
            if inb(x2, y2) and blocked(x2, y2):
                adj += 1

        # Tie-breaker: prefer reducing both-coordinate difference when pursuer, increasing when evader.
        dxy = abs(nx - ox) + abs(ny - oy)

        if i_am_pursuer:
            return (-dist, free, -adj, -dxy)
        else:
            return (dist, free, -adj, dxy)

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sc = score_move(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]

    return best_move