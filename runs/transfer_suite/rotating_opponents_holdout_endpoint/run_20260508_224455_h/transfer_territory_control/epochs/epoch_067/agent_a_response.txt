def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        adj_opt = ((nx - 1, ny) in opt) or ((nx + 1, ny) in opt) or ((nx, ny - 1) in opt) or ((nx, ny + 1) in opt)
        adj_my = ((nx - 1, ny) in myt) or ((nx + 1, ny) in myt) or ((nx, ny - 1) in myt) or ((nx, ny + 1) in myt)
        gain = 0
        if (nx, ny) in un:
            gain += 3
        elif (nx, ny) in opt:
            gain += 5  # flipping on entry
        if adj_opt:
            gain += 2
        if adj_my:
            gain += 1
        # prefer moves that cut off opponent growth by staying close to their boundary, but still moving forward
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_to_self = abs(nx - sx) + abs(ny - sy)
        score = (-gain, dist_to_opp, dist_to_self, nx, ny)
        cand.append((score, dx, dy))
    if not cand:
        return [0, 0]

    # Deterministic: pick best score; if equal, tuple order already breaks ties.
    cand.sort(key=lambda z: z[0])
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]