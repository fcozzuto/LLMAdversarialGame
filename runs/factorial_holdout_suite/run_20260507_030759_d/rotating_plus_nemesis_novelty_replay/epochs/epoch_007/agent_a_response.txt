def choose_move(observation):
    def get_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
            if "position" in v and isinstance(v["position"], (list, tuple)) and len(v["position"]) >= 2:
                return int(v["position"][0]), int(v["position"][1])
        return 0, 0

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = get_xy(observation.get("self_position"))
    ox, oy = get_xy(observation.get("opponent_position"))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o)
        obstacles.add((x, y))

    resources = [get_xy(r) for r in (observation.get("resources", []) or [])]
    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        tx, ty = 7, 7
        if sx <= 3 and sy <= 3:
            tx, ty = 0, 7
        best_m = [0, 0]
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            sc = -d
            if sc > best_s:
                best_s = sc
                best_m = [dx, dy]
        return best_m

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        immediate = 1 if (nx, ny) in res_set else 0
        min_self = 10**9
        best_diff = -10**9
        for rx, ry in resources:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            if sd < min_self:
                min_self = sd
            diff = od - sd  # higher if we are closer than opponent to that resource
            if diff > best_diff:
                best_diff = diff
        sc = immediate * 100000 + best_diff * 1000 - min_self
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best