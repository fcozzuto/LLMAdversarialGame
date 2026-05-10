def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_territory = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_territory.add((int(p[0]), int(p[1])))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                opp_terr.append((x, y))
    opp_set = set(opp_terr)

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                unclaimed.append((x, y))
    if not unclaimed:
        return [0, 0]

    # Target opponent frontier: unclaimed cells adjacent to opponent territory.
    opp_frontier = []
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for (x, y) in unclaimed:
        adj = False
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_set:
                adj = True
                break
        if adj:
            opp_frontier.append((x, y))

    # Fallback: nearest unclaimed.
    targets = opp_frontier if opp_frontier else unclaimed

    # Deterministic scoring: prefer cells that are closer; slight bias toward not-so-deep self territory.
    def score(t):
        tx, ty = t
        d = abs(tx - sx) + abs(ty - sy)
        bias = 0
        if (tx, ty) in self_territory:
            bias += 5
        return (d, bias, tx, ty)

    target = min(targets, key=score)
    tx, ty = target

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal would hit obstacle or out of bounds, try axis-aligned alternatives deterministically.
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if valid(nx, ny):
            return [int(mx), int(my)]
    return [0, 0]