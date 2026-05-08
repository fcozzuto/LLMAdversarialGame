def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_res = 10**9
        if resources:
            for rx, ry in resources:
                dd = abs(nx - rx) + abs(ny - ry)
                if dd < d_res:
                    d_res = dd

        sc = d_opp * 2
        if resources:
            sc -= d_res
        path = observation.get("self_path") or []
        if isinstance(path, (list, tuple)):
            if (nx, ny) in set(tuple(p) for p in path if isinstance(p, (list, tuple)) and len(p) >= 2):
                sc -= 5

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best