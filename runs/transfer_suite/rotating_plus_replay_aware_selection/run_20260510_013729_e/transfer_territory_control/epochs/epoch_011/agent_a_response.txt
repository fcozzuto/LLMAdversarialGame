def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    def neighbors_count(cx, cy, cellset):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = cx + ax, cy + ay
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in cellset:
                    c += 1
        return c

    center = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_sc = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in resources:
            sc += 200
        if (nx, ny) in self_ter:
            sc += 4 + neighbors_count(nx, ny, self_ter)
        if (nx, ny) in opp_ter:
            sc += 35 + 2 * neighbors_count(nx, ny, opp_ter) + 3 * neighbors_count(nx, ny, unclaimed)
        if (nx, ny) in unclaimed:
            sc += 18 + 2 * neighbors_count(nx, ny, unclaimed)
        # Move toward/along frontiers: adjacent to opponent/unclaimed while not stepping into safe self blobs only
        sc += 2 * neighbors_count(nx, ny, opp_ter)
        sc -= 0.5 * neighbors_count(nx, ny, self_ter)

        # Small deterministic tie-break: closer to center, then closer to nearest unclaimed
        dcx = abs(nx - center[0]) + abs(ny - center[1])
        if unclaimed:
            du = min(abs(cx - nx) + abs(cy - ny) for (cx, cy) in unclaimed)
        else:
            du = 0
        tie = (dcx, du)

        if best_sc is None or sc > best_sc or (sc == best_sc and tie < best):
            best_sc = sc
            best = tie
            best_move = [dx, dy]

    if best_sc is None:
        return [0, 0]
    return best_move