def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, cells):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in cells:
                c += 1
        return c

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    # If unclaimed exist, prefer moving to unclaimed/frontier; else switch to opponent pressure.
    prefer_unclaimed = (len(unclaimed) > 0)
    oppx, oppy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)
        score = 0

        # Base terrain desirability
        if cell in self_terr:
            score += 2
            score -= 0.2 * man(sx, sy, oppx, oppy)
        elif cell in unclaimed:
            score += 22
        elif cell in opp_terr:
            score += 14 if prefer_unclaimed else 22
            score += 0.5 * adj_count(nx, ny, self_terr)  # counter-claim into our surround
            score -= 0.3 * man(nx, ny, oppx, oppy)     # stay aggressive toward them
        else:
            score += 1 if cell in self_terr else 0

        # Frontier/adjacency shaping
        score += 2.5 * adj_count(nx, ny, unclaimed)
        score += 1.8 * adj_count(nx, ny, opp_terr)

        # Avoid getting pinned away from our territory expansion
        if prefer_unclaimed and self_terr:
            score += -0.15 * min(man(px, py, nx, ny) for (px, py) in self_terr) if len(self_terr) <= 20 else -0.15 * man(sx, sy, nx, ny)
        # Mild anti-stall penalty when far from any unclaimed
        if (dx == 0 and dy == 0) and prefer_unclaimed and unclaimed:
            dmin = min(man(u[0], u[1], sx, sy) for u in unclaimed)
            score -= 6 if dmin > 3 else 1

        # Deterministic tie-break toward lower dx, then dy preference
        tie = (0, dx, dy)
        if score > best_score or (score == best_score and (best is None or tie < best)):
            best_score = score
            best = tie
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]