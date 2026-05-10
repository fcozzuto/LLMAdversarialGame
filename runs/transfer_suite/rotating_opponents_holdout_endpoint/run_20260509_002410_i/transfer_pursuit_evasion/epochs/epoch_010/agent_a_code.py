def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, list):
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                res_list.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict) and "position" in r:
                pr = r["position"]
                if isinstance(pr, (list, tuple)) and len(pr) >= 2:
                    res_list.append((int(pr[0]), int(pr[1])))

    target = (ox, oy)
    if res_list:
        best = None
        bd = None
        for rx, ry in res_list:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if bd is None or d < bd or (d == bd and (rx, ry) < best):
                bd = d
                best = (rx, ry)
        if best is not None:
            target = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(target[0] - nx) + abs(target[1] - ny)
        # Prefer moves that reduce distance; tie-break deterministically by direction order.
        score = d * 1000 + (0 if (dx, dy) == (0, 0) else 1)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]