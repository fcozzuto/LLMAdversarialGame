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

    def has_opp_neighbor(cell):
        x, y = cell
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in opp_terr:
                    return True
        return False

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        score = 0.0
        if cell in unclaimed:
            score += 2.6
        if cell in self_terr:
            score += 0.2
        if cell in opp_terr:
            score += 4.2  # stepping into opponent territory flips
        if cell in unclaimed and has_opp_neighbor(cell):
            score += 1.8  # exploit contested boundary
        if cell[0] in (0, w - 1) or cell[1] in (0, h - 1):
            score += 0.5
        score += -0.06 * man(cell, opp_pos)  # keep pressure

        if score > best:
            best = score
            best_move = [dx, dy]
    return best_move