def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(dx, dy) for (dx, dy) in dirs if (dx, dy) != (0, 0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp_count(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx + dy

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in unclaimed
        is_opp = (nx, ny) in opp_terr
        is_self = (nx, ny) in self_terr

        d_opp = manh(nx, ny, ox, oy)
        adj_u = adj_unclaimed_count(nx, ny)
        adj_o = adj_opp_count(nx, ny)

        score = 0
        score += 10 * is_un
        score += 7 * is_opp
        score += 2 * is_self
        score += 0.8 * adj_u
        score += 1.2 * adj_o
        score += 2.5 / (1 + d_opp)  # prefer moving toward/near threat while expanding
        if (not is_un) and (not is_opp):  # don't wander on fully-taken space unless it borders expansion
            score -= 0.6 * (adj_u == 0)
        # strong deterrent: if we can capture adjacent to opponent, do it; otherwise don't chase deeper into their mass
        score += 1.0 * (adj_o >= 2) - 0.5 * (adj_o == 0)

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]