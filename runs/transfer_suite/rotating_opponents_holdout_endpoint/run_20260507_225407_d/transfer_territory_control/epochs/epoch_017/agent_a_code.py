def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(a, b, c, d): return abs(a - c) + abs(b - d)

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_adj = set()
    for px, py in opp_terr:
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in opp_terr and (nx, ny) not in obstacles:
                opp_adj.add((nx, ny))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = 0
        if (nx, ny) in resources:
            score += 9
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in self_terr:
            score += 1
        if (nx, ny) in opp_terr:
            score += 10  # flipping on entry
        if (nx, ny) in opp_adj:
            score -= 2  # likely near opponent frontier; avoid if possible
        d_opp = manh(nx, ny, ox, oy)
        score += d_opp * 0.6
        if (nx, ny) in opp_terr:
            score += (d_opp * 0.2)  # still allow capture
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            if best is None or (dx, dy) < (best[0], best[1]):
                best = [dx, dy]
    return [int(best[0]), int(best[1])]