def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(sx + dx, sy + dy) for dx, dy in dirs]
    neigh = [(x, y) for x, y in neigh if inside(x, y)]
    if not neigh:
        return [0, 0]

    opp_border = set()
    for x, y in opT:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                opp_border.add((nx, ny))

    frontier = []
    for x, y in selfT:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and ((nx, ny) in unT or (nx, ny) in opp_border):
                frontier.append((nx, ny))

    def score_cell(x, y):
        d_to_op = abs(x - ox) + abs(y - oy)
        is_un = (x, y) in unT
        is_op = (x, y) in opT
        is_f = (x, y) in opp_border or (x, y) in frontier
        # Prefer claiming new territory; also push onto opponent border lines.
        return (
            (5 if is_un else 0) +
            (8 if is_op else 0) +
            (3 if is_f else 0) -
            0.15 * d_to_op -
            0.01 * (abs(x - sx) + abs(y - sy))
        )

    targets = list(set(frontier)) if frontier else list(unT)
    if not targets:
        # If nothing known, move greedily toward opponent.
        best = min(neigh, key=lambda p: abs(p[0] - ox) + abs(p[1] - oy))
        return [best[0] - sx, best[1] - sy]

    best_next = neigh[0]
    best_val = -10**18
    for nx, ny in neigh:
        if (nx, ny) in opT:
            v = 10**9 + score_cell(nx, ny)
        else:
            # Choose next step that leads toward best target.
            # Deterministic local projection: prefer unclaimed/op-border cells and closer to chosen target.
            v = score_cell(nx, ny) - 0.07 * min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        if v > best_val:
            best_val = v
            best_next = (nx, ny)

    return [int(best_next[0] - sx), int(best_next[1] - sy)]