def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic order for tie-breaking
    res_list = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        res_list.append((rx, ry))
    res_list.sort()

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Evaluate by best immediate resource advantage (plus small distance penalty)
        cur_best = -10**18
        for tx, ty in res_list:
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            adv = do - ds  # positive if we are closer than opponent for this resource
            val = adv * 10 - ds * 0.25 + (-0.001 * (tx + 3 * ty))
            if val > cur_best:
                cur_best = val
        # Small preference to avoid moving away when no advantage exists
        overall = cur_best + dist(nx, ny, ox, oy) * (-0.02)

        if overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]