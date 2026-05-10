def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(p[0]), int(p[1])) for p in obstacles if p and len(p) >= 2}
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def nearest(pt_list, px, py):
        if not pt_list:
            return None
        best = pt_list[0]
        bd = abs(int(best[0]) - px) + abs(int(best[1]) - py)
        for p in pt_list[1:]:
            d = abs(int(p[0]) - px) + abs(int(p[1]) - py)
            if d < bd:
                bd = d
                best = p
        return (int(best[0]), int(best[1]))

    unclaimed = observation.get("unclaimed_cells", []) or []
    resources = observation.get("resources", []) or []

    target = nearest(unclaimed, x, y)
    if target is None:
        target = nearest(resources, x, y)
    if target is None:
        target = (ox, oy)

    tx, ty = target
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = int(x + dx), int(y + dy)
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        score = 0
        score -= abs(nx - tx) + abs(ny - ty)
        if (nx, ny) == (ox, oy):
            score += 1000000
        score += 3 if (nx, ny) in {(int(p[0]), int(p[1])) for p in unclaimed} else 0
        score += 2 if (nx, ny) in {(int(p[0]), int(p[1])) for p in resources} else 0
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = int(x + dx), int(y + dy)
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]