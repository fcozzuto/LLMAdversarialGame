def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    neigh8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if free(nx, ny): return [dx, dy]
        # deterministic fallback: try alternatives that are closer to target
        best = [0, 0]
        bestd = abs(sx - tx) + abs(sy - ty)
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: continue
                nx2, ny2 = sx + ddx, sy + ddy
                if not free(nx2, ny2): continue
                d2 = abs(nx2 - tx) + abs(ny2 - ty)
                if d2 < bestd or (d2 == bestd and (ddx, ddy) < tuple(best)):
                    bestd, best = d2, [ddx, ddy]
        return best

    targets = []
    if self_terr:
        for x, y in self_terr:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and (nx, ny) in unclaimed:
                    targets.append((nx, ny))
    if not targets and opp_terr:
        # pressure: move toward an unclaimed cell adjacent to opponent territory
        for x, y in opp_terr:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and (nx, ny) in unclaimed:
                    targets.append((nx, ny))

    if targets:
        tx, ty = min(targets, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        return step_towards(tx, ty)

    # last resort: go toward center, avoiding obstacles deterministically
    return step_towards(cx, cy)