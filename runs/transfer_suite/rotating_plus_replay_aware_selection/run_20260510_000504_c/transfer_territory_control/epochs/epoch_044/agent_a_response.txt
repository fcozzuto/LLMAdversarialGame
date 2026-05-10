def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if unclaimed:
        targets = unclaimed
        prefer_edge = True
    elif resources:
        targets = resources
        prefer_edge = False
    else:
        targets = list(opp_terr) if opp_terr else list(self_terr)
        prefer_edge = False

    opp_count = int(observation.get("opponent_territory_count", 0))
    self_count = int(observation.get("self_territory_count", 0))
    ahead = 1 if self_count > opp_count else 0

    best = None
    bx = by = 0

    def best_dist(x, y):
        bd = 10**9
        if prefer_edge:
            for (tx, ty) in targets[:48]:
                d = manhattan(x, y, tx, ty)
                if d < bd: bd = d
            return bd
        for (tx, ty) in targets[:48]:
            d = manhattan(x, y, tx, ty)
            if d < bd: bd = d
        return bd

    unclaimed_set = set(unclaimed)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = best_dist(nx, ny)
        cell = (nx, ny)
        score = -dist

        if unclaimed and cell in unclaimed_set:
            score += 40
        if cell in self_terr:
            score += 4 if ahead else 1
        if cell in opp_terr:
            score += 10 if not ahead else 2

        if prefer_edge:
            edge_bonus = 0
            if nx == 0 or nx == w - 1: edge_bonus += 2
            if ny == 0 or ny == h - 1: edge_bonus += 2
            score += edge_bonus

        # If we're ahead, slightly prefer moves that don't immediately expose by going toward opponent cells
        if ahead and opp_terr:
            d_to_opp = best_dist(nx, ny)
            if d_to_opp <= 2:
                score -= 6

        if best is None or score > best:
            best = score
            bx, by = dx, dy

    return [int(bx), int(by)] if best is not None else [0, 0]