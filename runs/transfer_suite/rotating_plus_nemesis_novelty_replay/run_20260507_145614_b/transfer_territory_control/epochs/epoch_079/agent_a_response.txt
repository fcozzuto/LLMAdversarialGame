def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((p[0], p[1]) for p in opp_terr if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles)
    self_set = set((p[0], p[1]) for p in self_terr if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles)

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def edge_bias(x, y):
        return (1 if x == 0 or x == w - 1 else 0) + (1 if y == 0 or y == h - 1 else 0)

    def adj_count(x, y, sset):
        c = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in sset:
                c += 1
        return c

    if unclaimed:
        best = None
        bestv = -10**18
        for x, y in unclaimed:
            if (x, y) in self_set or (x, y) in opp_set:
                continue
            aopp = adj_count(x, y, opp_set)
            aself = adj_count(x, y, self_set)
            d = abs(x - sx) + abs(y - sy)
            v = 10 * aopp + 5 * aself + 2 * edge_bias(x, y) - d
            if v > bestv or (v == bestv and (d < (abs(best[0] - sx) + abs(best[1] - sy)) if best else True)):
                bestv = v
                best = (x, y)
        tx, ty = best if best is not None else unclaimed[0]
    else:
        tx, ty = (w // 2, h // 2)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # deterministic fallback: try orthogonal/diagonal priority that avoids obstacles
        for ddx, ddy in ((dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy), (0, 0)):
            cx, cy = sx + ddx, sy + ddy
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                return [int(ddx), int(ddy)]
        return [0, 0]
    return [int(dx), int(dy)]