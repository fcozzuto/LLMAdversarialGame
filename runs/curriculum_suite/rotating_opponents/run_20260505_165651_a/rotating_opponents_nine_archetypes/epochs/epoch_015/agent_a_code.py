def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    scores = observation.get("scores", None)
    denier = False
    if isinstance(scores, (list, tuple)) and len(scores) >= 2:
        denier = scores[0] <= scores[1]

    if denier:
        tx, ty = min(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
    else:
        tx, ty = max(resources, key=lambda r: (man(ox, oy, r[0], r[1]) - man(sx, sy, r[0], r[1]), -man(sx, sy, r[0], r[1]), -abs(r[0] - (w - 1) / 2.0) - abs(r[1] - (h - 1) / 2.0), -r[0], -r[1]))
        tx, ty = int(tx), int(ty)

    moves = [(0, -1), (1, 0), (0, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        cd = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        score = -sd + 0.15 * od - 0.01 * cd
        if denier:
            score = score - 0.25 * man(nx, ny, ox, oy)
        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (best[0], best[1])):
            best_score = score
            best = (nx, ny, dx, dy)

    if best is None:
        return [0, 0]
    return [best[2], best[3]]