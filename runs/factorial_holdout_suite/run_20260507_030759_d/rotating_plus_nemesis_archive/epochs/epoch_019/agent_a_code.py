def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        return [0, 0]

    # Pick a target resource: prioritize where we can beat the opponent (reach sooner).
    best = None
    best_score = -10**18
    for r in res:
        tx, ty = int(r[0]), int(r[1])
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Higher is better: beat-ness dominates, then prefer closer.
        score = (do - ds) * 1000 - ds
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best

    # Choose move maximizing improvement toward target and avoiding obstacles.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d1 = md(nx, ny, tx, ty)
        d0 = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # prefer reducing distance; also prefer targets the opponent is farther from.
        val = (d0 - d1) * 1000 + (od - d1) - (1 if (nx, ny) == (ox, oy) else 0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move