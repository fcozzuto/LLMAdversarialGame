def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = observation.get("resources", []) or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_pos.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                res_pos.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                res_pos.append((int(r["x"]), int(r["y"])))
    if res_pos:
        tx, ty = min(res_pos, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dt = abs(tx - nx) + abs(ty - ny)
            do = abs(ox - nx) + abs(oy - ny)
            key = (dt, -do, dx, dy)
            if best is None or key < best:
                best = key
                best_move = [dx, dy]
        return best_move

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # No resources: move to reduce distance to opponent while avoiding obstacles.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(ox - nx) + abs(oy - ny)
        key = (d, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move if best is not None else [0, 0]