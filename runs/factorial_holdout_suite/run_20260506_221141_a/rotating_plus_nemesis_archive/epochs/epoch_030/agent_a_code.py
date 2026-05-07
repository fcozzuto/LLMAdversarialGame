def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources or not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def man(a, b, c, d): 
        return abs(a - c) + abs(b - d)

    # Target selection: maximize winning margin, prefer closer and safer (not immediately behind opponent).
    best = None
    for tx, ty in resources:
        my_d = man(sx, sy, tx, ty)
        op_d = man(ox, oy, tx, ty)
        margin = op_d - my_d
        # Boost resources where we are at least as fast with a small slack.
        slack_bonus = 2 if my_d <= op_d else 0
        key = (margin + slack_bonus, -my_d, -(tx + ty) if (tx + ty) % 2 == 0 else -(-tx - ty))
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine would keep in place
        my_d2 = man(nx, ny, tx, ty)
        op_d2 = man(ox, oy, tx, ty)
        # Prefer moving closer; if tie, keep improving our margin and avoid stepping "toward" opponent.
        # Since opponent position is static within turn, use its distance to target as context.
        margin_after = op_d2 - my_d2
        step_key = (-(my_d2), margin_after, -abs(nx - ox) - abs(ny - oy), -dx*dx - dy*dy)
        if best_move[0] is None or step_key > best_move[0]:
            best_move = (step_key, (dx, dy))
    dx, dy = best_move[1]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]