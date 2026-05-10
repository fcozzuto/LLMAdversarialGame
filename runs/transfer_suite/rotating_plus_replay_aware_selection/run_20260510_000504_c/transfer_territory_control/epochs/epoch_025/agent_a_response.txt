def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny))
        return out

    def front_set(base):
        out = set()
        for (x, y) in base:
            for (nx, ny) in neighbors8(x, y):
                if (nx, ny) in unclaimed:
                    out.add((nx, ny))
        return out

    self_front = front_set(self_terr) if self_terr else set()
    opp_front = front_set(opp_terr) if opp_terr else set()

    self_count = observation.get("self_territory_count", len(self_terr))
    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    going_defensive = opp_count > self_count

    if going_defensive and opp_front:
        targets = opp_front
    elif self_front:
        targets = self_front
    else:
        targets = unclaimed if unclaimed else set()

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_dist_to_targets(nx, ny):
        if not targets:
            return 0
        best = None
        for (tx, ty) in targets:
            d = dist(nx, ny, tx, ty)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 50
        if (nx, ny) in self_terr:
            score += 6
        if (nx, ny) in unclaimed:
            score += 10
        if targets and (nx, ny) in targets:
            score += 20
        if targets:
            score -= best_dist_to_targets(nx, ny)
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= abs(nx - cx) + abs(ny - cy) * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]