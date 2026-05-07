def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    target = None
    if resources:
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
            elif isinstance(r, dict) and "x" in r and "y" in r:
                rx, ry = int(r["x"]), int(r["y"])
            else:
                continue
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best:
                best = d
                target = (rx, ry)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        if target is not None:
            rx, ry = target
            val = abs(nx - ox) + abs(ny - oy) - (abs(nx - rx) + abs(ny - ry))
        else:
            val = (abs(nx - ox) + abs(ny - oy)) * -1
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]