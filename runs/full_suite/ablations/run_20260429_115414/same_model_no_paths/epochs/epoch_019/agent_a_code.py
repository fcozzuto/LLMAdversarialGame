def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Precompute nearest resource distances from each candidate position on the fly (small).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource desirability
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            res_score = -dmin
            if any(nx == rx and ny == ry for rx, ry in resources):
                res_score += 1000
        else:
            res_score = 0

        # Avoid opponent
        d_o = manh(nx, ny, ox, oy)
        opp_score = 0
        if d_o <= 1:
            opp_score -= 50
        else:
            opp_score += 0.5 * d_o

        # Deterministic tie-break by lexicographic direction weight
        move_score = res_score + opp_score
        if best is None or move_score > best_score:
            best_score = move_score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]