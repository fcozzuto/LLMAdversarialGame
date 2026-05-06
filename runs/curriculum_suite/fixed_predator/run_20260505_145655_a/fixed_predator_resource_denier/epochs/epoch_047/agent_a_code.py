def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a resource we can potentially "deny" (we want to be closer than opponent).
    best = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Primary: maximize opponent distance advantage; Secondary: minimize our distance.
        score = (od - sd) * 6 - sd
        # Mild tie-break toward nearer center to reduce deadlocks.
        center_bias = -((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2) * 0.0001
        t = (score + center_bias, sd, od, rx, ry)
        if best is None or t > best:
            best = t
    _, _, _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = dist(nx, ny, tx, ty)
        od2 = dist(nx, ny, ox, oy)  # closer to opponent generally helps denial, but not always
        # Favor reducing our distance to target, while keeping/creating separation from opponent.
        cand = (-(sd2), od2, -abs(nx - tx) - abs(ny - ty), dx, dy)
        candidates.append(cand)

    if not candidates:
        # All blocked; try staying.
        return [0, 0]

    candidates.sort(reverse=True)
    return [int(candidates[0][3]), int(candidates[0][4])]