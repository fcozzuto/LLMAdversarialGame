def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        target = min(unclaimed, key=lambda c: man((sx, sy), c))
    else:
        candidates = list(opp_terr) if opp_terr else [opp_pos]
        target = min(candidates, key=lambda c: man((sx, sy), c))

    def near_unclaimed(c):
        x, y = c
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    return True
        return False

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0.0
        if cell in unclaimed:
            score += 5.0
        if cell in opp_terr:
            score += 3.0
        if cell in self_terr:
            score += 1.0
        if near_unclaimed(cell):
            score += 2.0
        if cell not in self_terr:
            score += -0.15 * man(cell, target)
        else:
            score += 0.25
        score += -0.05 * man(cell, target)
        if score > best:
            best = score
            best_move = [dx, dy]
    return best_move