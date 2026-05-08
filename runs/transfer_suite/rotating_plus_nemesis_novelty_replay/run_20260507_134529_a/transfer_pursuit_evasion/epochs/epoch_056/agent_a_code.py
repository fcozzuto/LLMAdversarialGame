def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles")
    obstacles = set()
    if isinstance(obs, (list, tuple)):
        for p in obs:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            return -10**9
        d = abs(nx - ox) + abs(ny - oy)
        return d if self_is_evader else -d

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        sc = score_move(dx, dy)
        if sc > best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]