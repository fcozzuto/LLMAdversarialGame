def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unT = observation.get("unclaimed_cells") or []
    un = []
    for p in unT:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                un.append((x, y))

    if un:
        tx, ty = min(un, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy)) - 0.01 * (abs(c[0] - (w - 1) / 2.0) + abs(c[1] - (h - 1) / 2.0)) + abs(c[0] - sx) + abs(c[1] - sy))
    else:
        tx, ty = ox, oy

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    opts = [(dx, dy)]
    if dx == 0 or dy == 0:
        # deterministic tie-breakers for axis moves
        if dx == 0:
            opts += [(1, dy), (-1, dy), (0, 1), (0, -1)]
        else:
            opts += [(dx, 1), (dx, -1), (1, 0), (-1, 0)]
    # If blocked or out of bounds, try alternatives deterministically
    for a, b in opts:
        nx, ny = sx + a, sy + b
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [a, b]

    # Guaranteed fallback: try all 8 directions in fixed order
    for a, b in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + a, sy + b
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [a, b]
    return [0, 0]