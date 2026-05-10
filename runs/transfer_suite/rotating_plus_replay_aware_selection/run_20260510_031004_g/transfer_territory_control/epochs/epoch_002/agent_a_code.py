def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0.0

        if cell in unclaimed:
            score += 120.0
        if cell in opp_terr:
            score += 95.0
        if cell in self_terr:
            score -= 10.0

        # Move towards our best "attack corridor": cells that are closer to opponent than to us.
        d_to_opp = man(nx, ny, px, py)
        d_to_us = man(nx, ny, ox, oy)
        score += (16.0 - 1.2 * d_to_opp)

        # Prefer cutting directly toward opponent (diagonals help).
        score += 0.8 * (man(ox, oy, px, py) - man(nx, ny, px, py))

        # Slightly discourage staying if there is a better option.
        if dx == 0 and dy == 0:
            score -= 8.0

        # Deterministic tie-breaker: smallest (dx,dy) lex among equal scores.
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]