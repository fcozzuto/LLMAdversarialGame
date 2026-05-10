def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def role_is_evader():
        sr = str(observation.get("self_role") or "").lower()
        if "evader" in sr:
            return True
        if "pursuer" in sr or "chaser" in sr or "hunter" in sr:
            return False
        return False

    is_evader = role_is_evader()

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer a deterministic move ordering when scores tie
    # (knowing previous success, keep greedy but with obstacle-aware tie-breakers)
    order = []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            center_bias = -((nx - cx) ** 2 + (ny - cy) ** 2)  # closer to center is better for pursuer
            if is_evader:
                # evader: prefer staying far from center a bit to reduce chokepoints
                center_bias = ((nx - cx) ** 2 + (ny - cy) ** 2)
            order.append((dx, dy, center_bias, dist((nx, ny), (ox, oy))))
        else:
            order.append((dx, dy, -10**9, 10**9))

    if is_evader:
        # Evader: maximize distance; also avoid moves that reduce distance sharply.
        best = None
        best_key = None
        curd = dist((sx, sy), (ox, oy))
        for dx, dy, cb, nd in order:
            if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
                continue
            # tie-break: prefer moves that keep distance >= current when possible
            key = (nd, 1 if nd >= curd else 0, cb, -abs((sx + dx) - ox), -abs((sy + dy) - oy))
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Pursuer: minimize distance to opponent; if tied, move to center and then lexicographic order.
        best = None
        best_key = None
        for dx, dy, cb, nd in order:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
                continue
            key = (-nd, cb, -abs(nx - ox) - abs(ny - oy), -dx, -dy)  # deterministic tie-breaking
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]