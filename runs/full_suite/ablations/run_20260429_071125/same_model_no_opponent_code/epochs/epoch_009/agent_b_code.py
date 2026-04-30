def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            if "position" in v:
                q = v["position"]
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    return (int(q[0]), int(q[1]))
            if "x" in v and "y" in v:
                return (int(v["x"]), int(v["y"]))
        return default

    sx, sy = get_xy(observation.get("self_position", (0, 0)))
    ox, oy = get_xy(observation.get("opponent_position", (0, 0)))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        x, y = get_xy(p, None)
        if x is not None:
            obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        x, y = get_xy(p, None)
        if x is not None:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if resources:
        best = None
        for rx, ry in resources:
            d = abs(sx - rx) + abs(sy - ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        rx, ry = best[1]
        prefer = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            nd = abs(nx - rx) + abs(ny - ry)
            # break ties deterministically by opponent distance and then coordinates
            do = abs(nx - ox) + abs(ny - oy)
            prefer.append((nd, -do, nx, ny, dx, dy))
        if prefer:
            prefer.sort()
            return [prefer[0][4], prefer[0][5]]

    # No resources: deterministically move to reduce distance to opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        key = (d, -nx, -ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    if best is not None:
        return best[1]
    return [0, 0]