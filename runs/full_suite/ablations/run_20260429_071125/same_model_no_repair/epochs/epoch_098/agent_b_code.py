def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    resources = [tuple(p) for p in (observation.get("resources") or []) if p and len(p) >= 2 and tuple(p) not in obstacles]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        # Deterministic fallback: drift toward center to reduce losing by distance ties
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best_res = None
    best_key = (-10**9, 10**9, 10**9)  # (gain, my_dist, -res_index)
    for i, (rx, ry) in enumerate(resources):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        gain = opd - myd  # prefer resources we are closer to than opponent
        # Tie-break deterministically by closer first, then higher gain, then lower index
        key = (gain, myd, i)
        if best_res is None or (key[0], -key[1], -key[2]) > (best_key[0], -best_key[1], -best_key[2]):
            best_res = (rx, ry)
            best_key = key

    rx, ry = best_res
    # Choose a move that most improves our distance to target; break ties by increasing opponent distance to target.
    best_move = [0, 0]
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        # Additionally, if opponent is closer to the target, prefer moves that increase separation from opponent.
        sep = cheb(nx, ny, ox, oy)
        val = (-(myd2), myd2 + (0 if opd2 > myd2 else -1), sep, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move