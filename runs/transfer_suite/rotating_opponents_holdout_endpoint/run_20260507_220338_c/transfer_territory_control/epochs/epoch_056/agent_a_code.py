def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def norm(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            return int(p[0]), int(p[1])
        return None

    myT = set(filter(None, (norm(p) for p in (observation.get("self_territory") or []))))
    oppT = set(filter(None, (norm(p) for p in (observation.get("opponent_territory") or []))))
    unclaimed = set(filter(None, (norm(p) for p in (observation.get("unclaimed_cells") or []))))
    unclaimed -= obstacles

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_count(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in oppT:
                c += 1
        return c

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = 2.2 * (1 if (nx, ny) in unclaimed else 0)
        score += 1.0 * neigh_count(nx, ny)
        score -= 0.9 * adj_opp(nx, ny)  # avoid giving opponent a clean flip frontier
        score += 0.12 * (dist_opp)     # prefer moving away from opponent to reduce immediate contest
        # small bias to expand our boundary when possible
        if (nx, ny) not in myT:
            score += 0.15
        if score > bestv or (score == bestv and (dx, dy) < best):
            bestv = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]