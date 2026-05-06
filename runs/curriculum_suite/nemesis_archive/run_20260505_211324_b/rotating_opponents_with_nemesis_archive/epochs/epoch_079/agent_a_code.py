def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for o in (observation.get("obstacles") or []):
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        if sx == ox and sy == oy:
            score = man(nx, ny, ox, oy)
        elif res:
            score = -min(man(nx, ny, rx, ry) for rx, ry in res)
            score += 2 * man(nx, ny, ox, oy)
        else:
            score = 0
            score += 2 * man(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]