def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (ox, oy))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a deterministic target: prefer opponent cells, else unclaimed, else resources, else opponent position.
    cand = []
    for c in opp_t:
        if c not in obstacles:
            cand.append(c)
    if not cand:
        for c in unclaimed:
            if c not in obstacles:
                cand.append(c)
    if not cand:
        for c in resources:
            if c not in obstacles:
                cand.append(c)
    if not cand:
        cand = [(px, py)]

    best_target = None
    best_val = None
    for x, y in cand:
        ds = abs(x - ox) + abs(y - oy)
        do = abs(x - px) + abs(y - py)
        is_opp = (x, y) in opp_t
        val = ds - (4.0 if is_opp else 0.0) + 0.15 * do
        if best_val is None or val < best_val or (val == best_val and (x, y) < best_target):
            best_val = val
            best_target = (x, y)

    tx, ty = best_target

    # Choose move by immediate advantage + progress toward target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_target = abs(tx - nx) + abs(ty - ny)
        score = -dist_to_target

        if (nx, ny) in opp_t:
            score += 8.0  # likely flips control on entry
        elif (nx, ny) in unclaimed:
            score += 3.0  # claim new territory
        elif (nx, ny) in self_t:
            score += 0.25  # stable
        # slight bias to avoid moving backward along x/y to reduce dithering deterministically
        score -= 0.01 * (abs(nx - px) + abs(ny - py))

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (ox + best_move[0], oy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]