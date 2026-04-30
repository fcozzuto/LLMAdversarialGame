def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def adj_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    best = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we can take lead, but also avoid chasing when opponent is much closer.
        # If tie, prefer resource that is farther from opponent (denial via timing).
        lead = od - sd
        if sd == 0:
            key = (10**9, 0, 0, -adj_obs(rx, ry), rx, ry)
        else:
            key = (lead, -sd, -(od + sd), -abs(rx - ox) - abs(ry - oy), -adj_obs(rx, ry), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry), (sd, od))
    (rx, ry) = best[1]
    sd, od = best[2]

    # Move toward an "intercept" point: if opponent is closer, aim for a point just past one step toward resource
    # to potentially arrive at the same time or force a contested move.
    if od < sd:
        ix, iy = rx, ry
    else:
        ix = sx + (1 if rx > sx else -1 if rx < sx else 0)
        iy = sy + (1 if ry > sy else -1 if ry < sy else 0)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        nsd = dist(nx, ny, ix, iy)
        nod = dist(nx, ny, rx, ry)
        oppd = dist(ox, oy, rx, ry)
        # Prefer decreasing distance to intercept, avoid giving opponent immediate advantage, avoid obstacles.
        score = (
            -nsd,
            -(dist(nx, ny, rx, ry)),
            (oppd - dist(nx, ny, rx, ry)),  # increase our relative timing if possible
            -adj_obs(nx, ny),
            -(abs(nx - ox) + abs(ny - oy))
        )
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]