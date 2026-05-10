def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource we can beat (or get closest to beating)
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources where we arrive no later; tie-break for smaller own distance
        # If we can't win it, take the one with smallest "delay"
        can_win = 1 if myd <= opd else 0
        delay = (myd - opd)
        # Extra bias vs sweep_rows: prioritize resources on the opposite side in x from opponent
        x_bias = -abs(rx - (w - 1 - ox))
        key = (can_win, -delay, -myd, x_bias, rx, ry)  # deterministic
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move one step toward target; avoid obstacles; deterministic tie-break by delta order
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    # Prefer not to stay unless blocked by obstacles
    deltas.sort(key=lambda d: (0 if d != (0, 0) else 1, abs(d[0]) + abs(d[1]), d[0], d[1]))

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dcur = man(nx, ny, tx, ty)
        # slight repulsion from obstacles to avoid getting stuck
        near_obs = 0
        for ox2, oy2 in obs:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                near_obs = 1
                break
        val = (-dcur, -near_obs, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked, stay
    return [int(best_move[0]), int(best_move[1])]