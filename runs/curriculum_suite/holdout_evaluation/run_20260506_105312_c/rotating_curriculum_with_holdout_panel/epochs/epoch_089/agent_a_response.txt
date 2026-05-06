def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def step_to_center():
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return best[1] if best else (0, 0)

    if not resources:
        return [0, 0] if not obstacles else list(step_to_center())

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        lead_wins = 0
        min_da = 10**9
        min_do = 10**9
        closest_tie = 0
        for rx, ry in resources:
            da = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            if da < do:
                lead_wins += 1
            if da < min_da:
                min_da = da
            if do < min_do:
                min_do = do
            if da == do:
                closest_tie += 1

        # Encourage positions that put us in front of opponent for many resources,
        # and when tied, prefer smaller distance to our nearest resource.
        # Small penalty for staying adjacent to opponent to reduce direct contention.
        opp_adj = 1 if max(abs(nx - ox), abs(ny - oy)) == 1 else 0
        score = (lead_wins * 1000) - (min_da * 3) + (min_do) - (closest_tie * 10) - (opp_adj * 25)

        # Deterministic tie-break: higher score, then smaller min_da, then lex on (dx,dy)
        key = (-score, min_da, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]