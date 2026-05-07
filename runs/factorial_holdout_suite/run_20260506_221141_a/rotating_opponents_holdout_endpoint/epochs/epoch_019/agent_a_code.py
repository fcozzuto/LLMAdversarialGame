def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    has_resources = bool(resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if has_resources:
            md_opp = man(nx, ny, ox, oy)
            score += md_opp
            nr = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = man(nx, ny, rx, ry)
                if nr is None or d < nr:
                    nr = d
            if nr is None:
                score += 0
            else:
                score += 1000 - nr * 10
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    score += 50000
                    break
        else:
            score += man(nx, ny, ox, oy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move