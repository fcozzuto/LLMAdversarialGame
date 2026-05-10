def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position", [0, 0]))
    ox, oy = to_xy(observation.get("opponent_position", [sx, sy]))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    my_cells = set()
    for c in observation.get("self_path", []) or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            my_cells.add((int(c[0]), int(c[1])))

    op_cells = set()
    for c in observation.get("opponent_territory", []) or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            op_cells.add((int(c[0]), int(c[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    un_set = set()
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            un_set.add((int(c[0]), int(c[1])))

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obs:
            return -10**9
        if (x, y) in op_cells:
            return -10**6
        if (x, y) in un_set:
            return 10000 - (abs(x - sx) + abs(y - sy))
        d_opp = abs(x - ox) + abs(y - oy)
        return 200 - d_opp + (10 if (x, y) in my_cells else 0)

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best