def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def neigh4(x, y):
        return [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]

    def frontier_cells():
        fs = set()
        for (x, y) in opp_terr:
            for nx, ny in neigh4(x, y):
                if inb(nx, ny) and (nx, ny) not in obstacles and ((nx, ny) not in opp_terr):
                    fs.add((nx, ny))
        return fs

    front = frontier_cells()

    def best_score_for_cell(cell):
        if cell in obstacles:  # should not happen
            return -10**9
        if cell == (sx, sy):
            base = 0.0
        else:
            base = 0.0

        score = base
        if cell in unclaimed:
            score += 4.2
        if cell in self_terr:
            score += 0.7
        if cell in opp_terr:
            score += 3.8  # flipping on entry

        if cell in front:
            score += 2.8  # counterclaim potential

        # Distance pressure: expand toward nearest high-value targets
        if unclaimed:
            du = min(man(cell, c) for c in unclaimed)
            score += 1.6 / (1 + du)
        if opp_terr:
            do = min(man(cell, c) for c in opp_terr)
            score += 1.3 / (1 + do)
        score += 0.12 / (1 + man(cell, opp_pos))
        return score

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)
        candidates.append((best_score_for_cell(cell), -dx, -dy, dx, dy))

    candidates.sort(reverse=True)
    return [candidates[0][3], candidates[0][4]]