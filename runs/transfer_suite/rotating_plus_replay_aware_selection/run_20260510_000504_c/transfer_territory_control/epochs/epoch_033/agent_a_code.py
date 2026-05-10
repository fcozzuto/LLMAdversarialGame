def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    self_cnt = int(observation.get("self_territory_count", len(self_terr)))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)))
    behind = self_cnt < opp_cnt

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manh(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx + dy

    def has_neighbor_our(x, y):
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + ddx, y + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in self_terr:
                return True
        return False

    def has_neighbor_opp(x, y):
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + ddx, y + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in opp_terr:
                return True
        return False

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        if (nx, ny) == (ox, oy):
            return [dx, dy]

        score = 0
        if (nx, ny) in resources:
            score += 2000
        if (nx, ny) in unclaimed:
            score += 500
        if (nx, ny) in self_terr:
            score += 120
        if (nx, ny) in opp_terr:
            score += 80 if behind else 10
            score += 40 if has_neighbor_our(nx, ny) else 0

        if has_neighbor_our(nx, ny):
            score += 80
        if not behind and has_neighbor_opp(nx, ny) and (nx, ny) not in self_terr:
            score -= 120

        score += 30 * (-manh(nx, ny, ox, oy))  # generally approach opponent territory
        score -= 3 * manh(nx, ny, sx, sy)    # prefer less movement

        # small deterministic tie-breaker: prefer staying still when scores equal
        if score > best_score or (score == best_score and dx == 0 and dy == 0):
            best_score = score
            best = [dx, dy]

    return best