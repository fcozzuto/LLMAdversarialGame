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
        res = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                res.append((nx, ny))
        return res

    def front_adj(base):
        out = set()
        for x, y in base:
            for nx, ny in neighbors8(x, y):
                if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    out.add((nx, ny))
        return out

    self_front = front_adj(self_terr) if self_terr else set()
    opp_front = front_adj(opp_terr) if opp_terr else set()

    self_count = observation.get("self_territory_count", len(self_terr))
    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    going_defensive = opp_count > self_count

    candidates = []
    for tx, ty in opp_front:
        d = abs(tx - sx) + abs(ty - sy)
        steal_bias = 0 if not going_defensive else -2  # be more aggressive when behind
        candidates.append((0 + steal_bias, d, -tx, -ty, tx, ty))
    for tx, ty in self_front:
        d = abs(tx - sx) + abs(ty - sy)
        candidates.append((1, d, tx, ty, tx, ty))

    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, _, _, tx, ty = candidates[0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal is blocked by obstacle, try axis-aligned deterministically
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        if (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if (sx, sy + dy) not in obstacles:
            return [0, dy]
        if (sx, sy) not in obstacles:
            return [0, 0]
        return [0, 0]

    return [dx, dy]