def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in opp_terr:
            score += 30
        if (nx, ny) in self_terr:
            score -= 5

        score -= (abs(nx - ox) + abs(ny - oy)) * 0.1
        score += (4 - (abs(nx - px) + abs(ny - py))) * 1.5

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        nx, ny = ox + dx, oy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]

    return [0, 0]