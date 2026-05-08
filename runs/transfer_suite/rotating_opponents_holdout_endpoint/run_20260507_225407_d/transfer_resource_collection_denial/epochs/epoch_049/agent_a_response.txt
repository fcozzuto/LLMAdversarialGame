def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]
    if any(x == sx and y == sy for x, y in res):
        return [0, 0]

    # pick target that maximizes our advantage in arrival time
    best = None
    best_key = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        td = man(ox, oy, tx, ty)
        key = (td - sd, -sd, -td, -(tx + ty))
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)
    tx, ty = best

    # greedy one-step: choose next move that maximizes future advantage and reduces distance to target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if nx == tx and ny == ty:
            return [dx, dy]
        our = man(nx, ny, tx, ty)
        opp = man(ox, oy, tx, ty)
        key = ((opp - our), -our, -opp, -abs(nx - tx) - abs(ny - ty))
        if best_move_key is None or key > best_move_key:
            best_move_key, best_move = key, [dx, dy]

    return best_move