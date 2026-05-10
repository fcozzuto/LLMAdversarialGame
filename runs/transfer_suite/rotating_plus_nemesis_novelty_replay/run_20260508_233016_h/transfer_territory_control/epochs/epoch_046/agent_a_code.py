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

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    def adj8(c):
        x, y = c
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield (nx, ny)

    opp_front = set()
    for t in opp_terr:
        for n in adj8(t):
            if n in unclaimed:
                opp_front.add(n)

    self_front = set()
    for t in self_terr:
        for n in adj8(t):
            if n in unclaimed:
                self_front.add(n)

    candidates = list(opp_front) if opp_front else (list(self_front) if self_front else list(unclaimed))
    if candidates:
        target = min(candidates, key=lambda c: (dist((sx, sy), c), c[0], c[1]))
    else:
        target = opp_pos

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        score = 0.0
        if cell in opp_terr:
            score += 8.0
        if cell in unclaimed:
            score += 4.0
            if any(n in self_terr for n in adj8(cell)):
                score += 1.2
            if any(n in opp_terr for n in adj8(cell)):
                score += 1.6
        if cell in self_terr:
            score += 0.8

        d1 = dist(cell, target)
        d2 = dist((sx, sy), target)
        score += (d2 - d1) * 1.2

        score += -0.02 * dist(cell, opp_pos)
        score += 0.001 * (dx * 3 + dy)

        key = (score, -abs(dx) - abs(dy), -((dx == 0 and dy == 0)))
        if key > best:
            best = key
            best_move = [dx, dy]

    return best_move