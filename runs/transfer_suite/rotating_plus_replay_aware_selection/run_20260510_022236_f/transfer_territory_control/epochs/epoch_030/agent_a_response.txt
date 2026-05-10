def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
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

    if not unclaimed:
        return [0, 0]

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    best_t = None
    best_sc = -10**18
    for tx, ty in unclaimed:
        dus = abs(tx - sx) + abs(ty - sy)
        doo = abs(tx - ox) + abs(ty - oy)
        edge_bias = (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1)
        sc = (doo - dus) * 10 - dus + (0.2 if edge_bias else 0.0)
        if best_t is None or sc > best_sc:
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_ms = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (tx, ty):
            ns = 10**12
        else:
            dus = abs(tx - nx) + abs(ty - ny)
            doo = abs(tx - ox) + abs(ty - oy)
            ns = -dus * 2 + doo * 0.05
        if ns > best_ms:
            best_ms = ns
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]