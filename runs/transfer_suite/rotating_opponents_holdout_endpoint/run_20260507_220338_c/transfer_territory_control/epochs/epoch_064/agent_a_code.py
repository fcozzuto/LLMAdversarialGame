def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        # Deterministic tie-break: prefer moves with smaller dx, then dy
        val = (d, dx, dy)
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]