def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_step = (0, 0)
    best_val = -10**18

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_self = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(ox - nx) + abs(oy - ny)
            val = -d_self + 0.05 * d_opp
            if val > best_val:
                best_val, best_step = val, [dx, dy]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_opp = abs(ox - nx) + abs(oy - ny)
            d_ctr = abs((w - 1) / 2.0 - nx) + abs((h - 1) / 2.0 - ny)
            val = d_opp - 0.01 * d_ctr
            if val > best_val:
                best_val, best_step = val, [dx, dy]

    return [int(best_step[0]), int(best_step[1])]