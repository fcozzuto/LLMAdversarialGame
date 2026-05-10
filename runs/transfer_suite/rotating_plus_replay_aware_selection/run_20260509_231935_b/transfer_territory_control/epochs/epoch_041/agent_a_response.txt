def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    idx = int(observation.get("turn_index", 0)) % len(dirs)
    dirs = dirs[idx:] + dirs[:idx]

    self_name = observation["self_name"]
    opp_name = observation["opponent_name"]
    scores = observation.get("scores") or {}
    self_score = scores.get(self_name, 0.0) if isinstance(scores, dict) else 0.0
    opp_score = scores.get(opp_name, 0.0) if isinstance(scores, dict) else 0.0

    need_recover = (observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0)) or (self_score < opp_score)
    targets = (list(opp_terr) if need_recover else list(unclaimed))
    if not targets:
        targets = list(unclaimed) if unclaimed else list(opp_terr)
    if not targets:
        targets = [(w // 2, h // 2)]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    tx, ty = sx, sy
    bestd = 10**9
    for x, y in targets:
        d = manhattan(x, y, sx, sy)
        if d < bestd or (d == bestd and (x < tx or (x == tx and y < ty))):
            bestd = d
            tx, ty = x, y

    def cell_value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in self_terr:
            return 0.0
        if (nx, ny) in opp_terr:
            return 2.0 if need_recover else 1.2
        if (nx, ny) in unclaimed:
            return 2.4 if not need_recover else 1.6
        return 0.6

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        d = manhattan(nx, ny, tx, ty)
        val = -d + cell_value(nx, ny)
        if dx == 0 and dy == 0:
            val -= 0.15
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]