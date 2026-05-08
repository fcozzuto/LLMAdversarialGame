def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x, y):
        dx, dy = x - ox, y - oy
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def obstacle_pen(x, y):
        # Higher penalty means worse (avoid getting close to obstacles)
        if not obs:
            return 0
        best = 999
        for px, py in obs:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        # penalty spikes when adjacent
        if best <= 1:
            return 6
        if best == 2:
            return 3
        return 0

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_pursuer:
        # Pursuer targets the corner that is nearest to the evader (to herd)
        target_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = target_corner
        best_val = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            val = cheb(nx, ny)
            # If tied on closing distance, move toward the herd corner
            val = val * 10 + (abs(nx - tx) + abs(ny - ty))
            val += obstacle_pen(nx, ny)
            if best_val is None or val < best_val or (val == best_val and (dx, dy) < tuple(best_move)):
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Evader: maximize distance to pursuer, also bias toward farthest corner
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tx, ty = target_corner
    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        val = cheb(nx, ny)
        val = val * 10 + (abs(nx - tx) + abs(ny - ty))  # prefer being far from herd corner
        val -= obstacle_pen(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]
    return best_move