def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Build candidate frontier targets deterministically
    frontier = []
    if self_terr:
        for (x, y) in self_terr:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if free(nx, ny) and (nx, ny) in unclaimed:
                    frontier.append((nx, ny))
    else:
        frontier = list(unclaimed)

    # Prefer capturing unclaimed adjacent to our territory; otherwise pressure opponent
    best_target = None
    if frontier:
        best_target = min(frontier, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        # Pressure: move toward a cell adjacent to opponent territory (to enable flipping)
        pressure = []
        for (x, y) in opp_terr:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if free(nx, ny) and ((nx, ny) not in self_terr):
                    pressure.append((nx, ny))
        if pressure:
            best_target = min(pressure, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    # Choose best step minimizing distance to target; bias toward moving into unclaimed
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = (10**9, 10**9, 10**9, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        into_unclaimed = 1 if (nx, ny) in unclaimed else 0
        # If stepping onto opponent territory, it should flip; prefer only if it reduces distance
        into_opp = 1 if (nx, ny) in opp_terr else 0
        # Deterministic tie-break: prefer higher into_unclaimed, then into_opp, then lexicographic move
        key = (dist, -into_unclaimed, -into_opp, dx if dx != 0 else dy)
        if key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]