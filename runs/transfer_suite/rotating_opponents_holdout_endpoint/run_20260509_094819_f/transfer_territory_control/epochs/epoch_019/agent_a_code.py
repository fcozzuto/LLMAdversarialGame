def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed = [tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]
    unclaimed_set = set(unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    target = None
    bestd = 10**9
    for cx, cy in unclaimed:
        d = abs(cx - sx) + abs(cy - sy)
        if d < bestd:
            bestd = d
            target = (cx, cy)

    if target is None:
        target = (ox, oy)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        val = 0
        if cell in opp_terr:
            val += 200
        elif cell in unclaimed_set:
            val += 40
        elif cell in self_terr:
            val += 10
        d = abs(target[0] - nx) + abs(target[1] - ny)
        val -= d
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move