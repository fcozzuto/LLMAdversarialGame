def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        return [0, 0]

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target: close to us, far from opponent, preferably edges.
    best_target = None
    best_tkey = None
    for tx, ty in unclaimed:
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        ds = dist((sx, sy), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        edge = 0
        if tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1:
            edge = 1
        # minimize (ds - 0.6*do - edge*2 - small tie-break)
        tkey = ds - 0.6 * do - 2.0 * edge + 0.01 * (tx + ty)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (tx, ty)

    tx, ty = best_target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_eval = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        nd = dist((nx, ny), (tx, ty))
        curd = dist((sx, sy), (tx, ty))
        # Encourage cutting into opponent territory; also prefer reducing distance.
        flip_bonus = 4.0 if (nx, ny) in opp_set else 0.0
        edge_next = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
        evalv = -nd + 0.35 * (curd - nd) + flip_bonus + 0.3 * edge_next
        if best_eval is None or evalv > best_eval:
            best_eval = evalv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]