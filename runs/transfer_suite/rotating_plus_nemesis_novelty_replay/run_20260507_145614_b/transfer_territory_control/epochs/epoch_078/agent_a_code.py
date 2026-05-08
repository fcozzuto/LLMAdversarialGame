def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if best_d is None or d < best_d:
            best_d = d
            best = (dx, dy)
    if best is None:
        return [0, 1] if sy + 1 < h else [1, 0] if sx + 1 < w else [0, -1] if sy - 1 >= 0 else [-1, 0]
    return [best[0], best[1]]