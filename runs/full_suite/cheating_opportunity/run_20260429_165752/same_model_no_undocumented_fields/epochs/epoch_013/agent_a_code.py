def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            ox2, oy2 = int(o[0]), int(o[1])
            if 0 <= ox2 < w and 0 <= oy2 < h:
                obs.add((ox2, oy2))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_t = resources[0]
    best_d = man(x, y, best_t[0], best_t[1])
    for rx, ry in resources[1:]:
        d = man(x, y, rx, ry)
        if d < best_d:
            best_d, best_t = d, (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def min_dist_to_resources(px, py):
        md = None
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    best_move = moves[4]
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy):
            continue
        d_to_res = min_dist_to_resources(nx, ny)
        d_to_opp = man(nx, ny, ox, oy)
        score = d_to_res * 10 - d_to_opp
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]