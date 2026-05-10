def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    def score_cell(cell):
        x, y = cell
        s = 0.0
        if cell in unclaimed:
            s += 3.2
        if cell in self_terr:
            s += 0.3
        if cell in opp_terr:
            s += 6.2  # flipping opponent territory on entry
        if cell in obstacles:
            s -= 1000.0
        # Drive toward center, but slightly favor closer-than-opponent center pressure
        dc = abs(x - cx) + abs(y - cy)
        s += (10.0 - dc) * 0.35
        odc = abs(opp_pos[0] - cx) + abs(opp_pos[1] - cy)
        s += (odc - dc) * 0.25
        # Avoid getting stuck near obstacles
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                s -= 0.15
        # Prefer moving closer to nearest unclaimed if it exists
        if unclaimed:
            nu = min(unclaimed, key=lambda c: dist((x, y), c))
            s += max(0.0, 6.0 - dist((x, y), nu)) * 0.45
        # Prefer increasing distance from opponent a bit unless flipping
        if cell not in opp_terr:
            s += dist((x, y), opp_pos) * 0.05
        # Prefer not to stay still unless it's best
        if (x, y) == (sx, sy):
            s -= 0.8
        return s

    best_s = -10**18
    best = [0, 0]
    parity = observation.get("turn_index", 0) % 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        s = score_cell((nx, ny))
        # Deterministic tie-breaker: favor diagonal on parity alternation
        tie = 0.0
        if dx != 0 and dy != 0:
            tie = 0.06 if parity == 0 else -0.02
        elif dx == 0 and dy == 0:
            tie = -0.02
        s += tie
        if s > best_s:
            best_s = s
            best = [dx, dy]
    return best