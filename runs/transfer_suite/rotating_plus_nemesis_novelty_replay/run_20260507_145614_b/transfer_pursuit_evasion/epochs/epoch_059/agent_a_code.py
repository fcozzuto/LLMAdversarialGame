def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    srole = (observation.get("self_role") or "").lower()
    evader = ("evader" in srole) or ("evasion" in srole) or ("runner" in srole)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            val = d2 if evader else -d2
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best = (dx, dy)
                best_val = val
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]