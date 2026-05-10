def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_cells = set((p[0], p[1]) for p in observation.get("self_territory", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    neigh8 = moves
    def is_on_edge(x, y):
        return x == 0 or y == 0 or x == w - 1 or y == h - 1
    def cell_score(x, y):
        if not inside(x, y):
            return -10**12
        if (x, y) in self_cells:
            base = -2
        elif (x, y) in opp_cells:
            md = abs(x - ox) + abs(y - oy)
            base = 120 - 4 * md
        elif (x, y) in unclaimed:
            md = abs(x - ox) + abs(y - oy)
            base = 35 - 2.5 * md
        else:
            base = -3
        # Break ties: prefer progressing toward opponent and building edge pressure
        toward = -(abs(x - ox) + abs(y - oy))
        edge = 8 if is_on_edge(x, y) else 0
        # Small penalty for being surrounded by obstacles/occupied to reduce stalls
        block = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                block += 1
        base += toward + edge - 0.6 * block
        # If we can flip into opponent territory, strongly prefer doing it now
        if (x, y) in opp_cells:
            base += 50
        return base
    best_score = -10**18
    best = (0, 0)
    # Deterministic tie-break: fixed order of moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best_score:
            best_score = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]