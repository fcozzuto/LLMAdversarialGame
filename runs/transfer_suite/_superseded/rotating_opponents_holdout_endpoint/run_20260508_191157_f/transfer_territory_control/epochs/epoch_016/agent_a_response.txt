def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_adj = set()
    for (x, y) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inside(nx, ny):
                    opp_adj.add((nx, ny))

    candidates = [p for p in unclaimed if p in opp_adj]
    if not candidates:
        candidates = list(unclaimed)
    if candidates:
        tx, ty = min(candidates, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_terr:
            return 1000000
        if (x, y) in unclaimed:
            return 200000
        if (x, y) in self_terr:
            return 0
        return 50000

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        score = cell_value(nx, ny)
        dist = abs(nx - tx) + abs(ny - ty)
        score += -dist * 10
        score += -max(0, dist - 1) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]