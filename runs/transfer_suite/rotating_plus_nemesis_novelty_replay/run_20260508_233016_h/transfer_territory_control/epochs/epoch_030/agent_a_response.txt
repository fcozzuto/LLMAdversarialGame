def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])
    cx, cy = w // 2, h // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        target = min(unclaimed_list, key=lambda c: man((sx, sy), c))
    else:
        target = (cx, cy)

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        score = 0.0
        if cell in unclaimed:
            score += 3.5
        if cell in self_terr:
            score += 0.6
        if cell in opp_terr:
            score += 2.2  # flipping on entry
        if cell == (sx, sy) and (dx, dy) == (0, 0):
            score -= 0.15

        score += 0.18 * (man(target, (sx, sy)) - man(target, cell))  # progress to target
        score += 0.08 * (man((cx, cy), cell))  # drift toward center away from edge-clamper
        score -= 0.10 * man(opp_pos, cell)  # avoid getting trapped at opponent edge

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best