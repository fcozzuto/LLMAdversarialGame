def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    # Target selection: prefer resources where we arrive earlier; break ties by shorter my distance.
    best = None
    best_key = None
    for rx, ry in res:
        my_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        key = (my_d - opp_d, my_d, abs(rx - (w - 1 - ox)) + abs(ry - (h - 1 - oy)))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move selection: local obstacle-aware greedy toward target with contest-aware tie-breaking.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to_t = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        my_d_after = abs(tx - nx) + abs(ty - ny)
        # Encourage improving contest (smaller my_d_after vs opp_d), also keep moving toward target.
        key = (my_d_after - opp_d, my_to_t, abs(nx - tx) + abs(ny - ty))
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move if best_move_key is not None else [0, 0]