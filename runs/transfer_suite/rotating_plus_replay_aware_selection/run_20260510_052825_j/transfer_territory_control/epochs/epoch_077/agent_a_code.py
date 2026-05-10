def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p is not None and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p is not None and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p is not None and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p is not None and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_cell(cx, cy):
        if not inb(cx, cy) or (cx, cy) in obstacles:
            return -10**9
        # primary: expand into unclaimed; secondary: take opponent boundary; tertiary: keep momentum
        s = 0
        if (cx, cy) in unclaimed:
            s += 200
        if (cx, cy) in oppT:
            s += 80
        if (cx, cy) in selfT:
            s += 10

        # frontier pressure: how many attractive neighbors around target
        frontier = 0
        opp_adj = 0
        for dx, dy in neigh_dirs:
            nx, ny = cx + dx, cy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    frontier += 1
                elif (nx, ny) in oppT:
                    opp_adj += 1
        s += frontier * 30
        s += opp_adj * 40

        # distance to opponent territory (attract towards boundary if opponent exists)
        if oppT:
            best = 10**9
            for ox, oy in oppT:
                d = abs(ox - cx) + abs(oy - cy)
                if d < best:
                    best = d
            s -= best * 4
        return s

    # If we can immediately claim an unclaimed cell, do it deterministically
    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        candidates.append((score_cell(nx, ny), dx, dy))
    candidates.sort(reverse=True)  # score first, then dx/dy due to tuple order
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]