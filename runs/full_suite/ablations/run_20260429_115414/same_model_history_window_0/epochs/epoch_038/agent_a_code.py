def choose_move(observation):
    gw, gh = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs_set.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    cx, cy = (gw - 1) // 2, (gh - 1) // 2
    if not resources:
        tx, ty = cx, cy
    else:
        parity = int(observation.get("turn_index", 0)) & 1
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs_set:
                continue
            ds = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
            do = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            # Prefer locations where opponent is further than us (do - ds larger), then closer to us
            score = (-(do - ds), ds + parity * 1e-9)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = (best[1], best[2]) if best else (cx, cy)

    best_move = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        ds = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Also slightly prefer moving away from opponent when tie
        key = (ds, -(do))
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]