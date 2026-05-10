def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    else:
        tx, ty = px, py

    best_key = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_opp = abs(nx - px) + abs(ny - py)
        dist_focus = abs(nx - tx) + abs(ny - ty)

        if (nx, ny) in opp_terr:
            score = 5000 - dist_opp
        else:
            score = 0
            if (nx, ny) in unclaimed:
                score += 350
            if (nx, ny) in resources:
                score += 220
            if (nx, ny) in self_terr:
                score -= 25
            score += -dist_opp * 3
            score += -dist_focus * 2

        key = (score, -dist_opp, -dist_focus, -dx, -dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]