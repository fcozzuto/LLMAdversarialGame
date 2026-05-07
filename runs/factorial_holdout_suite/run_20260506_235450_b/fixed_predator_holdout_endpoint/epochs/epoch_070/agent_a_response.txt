def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    if not resources:
        return [0, 0]

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Choose move that maximizes relative progress: (opponent_distance - my_distance)
        # Tie-break: smaller my_distance.
        best_key = (-10**9, 10**9)
        for tx, ty in res:
            my_d = manh(nx, ny, tx, ty)
            opp_d = manh(ox, oy, tx, ty)
            key = (opp_d - my_d, my_d)
            if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] < best_key[1]):
                best_key = key

        # Slightly prefer moves that reduce my distance to the best target
        if best_key[0] > best[1] or (best_key[0] == best[1] and best[0] is not None):
            pass
        score = best_key[0] * 100 - best_key[1]
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]