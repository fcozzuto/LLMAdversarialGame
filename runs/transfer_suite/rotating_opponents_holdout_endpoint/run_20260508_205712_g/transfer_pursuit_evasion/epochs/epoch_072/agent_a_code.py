def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    sr = str(observation.get("self_role") or "").lower()
    is_evader = not (("pursuer" in sr) or ("pred" in sr) or ("catch" in sr) or ("hunter" in sr))

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = -d if not is_evader else d
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif val == best_val and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]