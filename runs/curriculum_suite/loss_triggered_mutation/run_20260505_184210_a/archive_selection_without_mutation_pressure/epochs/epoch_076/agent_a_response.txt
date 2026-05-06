def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [])
    resources = [tuple(r) for r in (observation.get("resources") or []) if isinstance(r, (list, tuple)) and len(r) == 2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        # drift toward center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, cx, cy)
            key = (d, man(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Predict opponent's greedy target: nearest remaining resource
    def opp_target():
        best = None
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    tx, ty = opp_target()

    # Choose move to maximize capture likelihood (reduce my distance vs opponent), with tie-breakers
    opp_now = man(ox, oy, tx, ty)
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_d = man(nx, ny, tx, ty)
        rel = my_d - opp_now  # negative is good
        # If I can't beat them, try to deny by heading toward the second-closest resource to me
        alt_d = 10**9
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            d = man(nx, ny, rx, ry)
            if d < alt_d:
                alt_d = d
        # also discourage stepping onto squares that are close to opponent's current path target
        opp_steps = man(nx, ny, ox, oy)
        key = (-rel, -my_d, alt_d, opp_steps, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]