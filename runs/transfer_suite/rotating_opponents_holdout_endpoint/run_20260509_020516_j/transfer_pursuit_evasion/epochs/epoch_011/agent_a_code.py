def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        # Worst-case opponent response: it chooses a valid move that maximizes distance from our next position.
        worst_dist = -1
        worst_opp = (0, 0)
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            dist = d2(tx, ty, nx, ny)
            if dist > worst_dist or (dist == worst_dist and (odx, ody) < worst_opp):
                worst_dist = dist
                worst_opp = (odx, ody)

        # Secondary objective: keep our mobility high to avoid getting zigzag-locked.
        mob = 0
        for ddx, ddy in deltas:
            xx, yy = nx + ddx, ny + ddy
            if valid(xx, yy):
                mob += 1

        key = (worst_dist, -mob, mdx, mdy)
        if best is None or key < best:
            best = key
            best_move = [mdx, mdy]

    return [int(best_move[0]), int(best_move[1])]