def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("resources") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    if not self_terr:
        self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        target = min(unclaimed, key=lambda c: man(c, (sx, sy)))
    else:
        target = (w // 2, h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    dirs_order = moves

    for dx, dy in dirs_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0
        if cell in unclaimed:
            score += 14
        if cell in opp_terr:
            score += 10
        if cell in self_terr:
            score += 3
        score += 0.6 * (man(cell, (ox, oy)) * -1) + 0.6 * man(cell, (target[0], target[1]))
        score += 0.001 * (nx - sx) + 0.0001 * (ny - sy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]