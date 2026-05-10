def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (ox, oy))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neighbors(x, y):
        for dx, dy in adj8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                yield nx, ny

    # Build targets: unclaimed adjacent to opponent territory, else opponent territory, else resources, else unclaimed
    opp_adj_unclaimed = []
    for x, y in opp_terr:
        for nx, ny in neighbors(x, y):
            if (nx, ny) in unclaimed:
                opp_adj_unclaimed.append((nx, ny))
    opp_adj_unclaimed = list(dict.fromkeys(opp_adj_unclaimed))

    targets = []
    if opp_adj_unclaimed:
        targets = opp_adj_unclaimed
    elif opp_terr:
        targets = list(opp_terr)
    elif resources:
        targets = list(resources)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(px, py)]

    def score_cell(tx, ty):
        d = max(abs(tx - ox), abs(ty - oy))
        # Prefer moving directly into opponent territory (flipping)
        in_opp = (tx, ty) in opp_terr
        in_res = (tx, ty) in resources
        # Prefer nearer to opponent to counterclaim; tie-break deterministically by coords
        return ((-1 if in_opp else 0, -1 if in_res else 0),
                d,
                abs(tx - px) + abs(ty - py),
                tx, ty)

    target = min(targets, key=lambda c: score_cell(c[0], c[1]))

    best = None
    bestmove = (0, 0)
    for dx, dy in dirs8:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = max(abs(target[0] - nx), abs(target[1] - ny))
        enters_opp = (nx, ny) in opp_terr
        enters_uncl = (nx, ny) in unclaimed
        s = (0 if enters_opp else 1, 0 if enters_uncl else 1, d, nx, ny)
        if best is None or s < best:
            best = s
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]