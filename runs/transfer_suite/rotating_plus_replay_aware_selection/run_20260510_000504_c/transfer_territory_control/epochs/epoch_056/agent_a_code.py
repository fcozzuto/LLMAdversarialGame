def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    opp_terr = observation.get("opponent_territory") or []
    self_terr = observation.get("self_territory") or []
    self_set = set(map(tuple, self_terr))
    opp_set = set(map(tuple, opp_terr))
    unclaimed_set = set(map(tuple, unclaimed))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in opp_set:
            return 120  # flipping opponent cell is strongly good
        if (nx, ny) in unclaimed_set:
            return 90
        if (nx, ny) in self_set:
            return 30
        return 10  # other squares (should be rare)

    # Prefer capturing adjacent frontier around our territory
    frontier = []
    for (x, y) in self_set:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed_set:
                frontier.append((nx, ny))
            elif inb(nx, ny) and (nx, ny) in opp_set:
                frontier.append((nx, ny))
    frontier = list(dict.fromkeys(frontier))[:32]

    # Deterministic target heuristic
    candidates = []
    if frontier:
        targets = frontier
    elif unclaimed:
        targets = list(unclaimed)
    elif resources:
        targets = list(resources)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(w - 1, h - 1)]

    tx0, ty0 = targets[0]
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        if d < abs(tx0 - sx) + abs(ty0 - sy) or (d == abs(tx0 - sx) + abs(ty0 - sy) and (ty < ty0 or (ty == ty0 and tx < tx0))):
            tx0, ty0 = tx, ty

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
            if (nx, ny) in obstacles:
                return [0, 0]
        val = step_score(nx, ny)
        # Pull towards nearest chosen target while keeping frontier priority
        val += - (abs(nx - tx0) + abs(ny - ty0))
        # Small deterministic preference to move right/up to break ties
        val += (dx + dy) * 0.001
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]
    return best_move