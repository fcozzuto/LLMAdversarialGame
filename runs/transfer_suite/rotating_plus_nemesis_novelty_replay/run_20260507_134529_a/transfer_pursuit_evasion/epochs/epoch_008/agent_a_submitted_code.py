def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    want_approach = ("evader" not in roles) or ("pursuer" in roles)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        val = d if not want_approach else -d
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0] if valid(sx, sy) else ([-1, 0] if valid(sx - 1, sy) else [0, 1] if valid(sx, sy + 1) else [1, 0] if valid(sx + 1, sy) else [0, -1] if valid(sx, sy - 1) else [0, 0]])