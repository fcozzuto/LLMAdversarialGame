def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    opp_boundary = set()
    for (x, y) in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and ((nx, ny) in unclaimed):
                    opp_boundary.add((nx, ny))

    targets = resources if resources else (list(unclaimed) if unclaimed else [])
    if not targets and opp_boundary:
        targets = list(opp_boundary)
    if not targets:
        targets = [(ox, oy)]

    def mindist(a, target_list):
        ax, ay = a
        md = 10**9
        for tx, ty in target_list:
            d = abs(ax - tx) + abs(ay - ty)
            if d < md:
                md = d
        return md

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cell = (nx, ny)
        cap = 0.0
        if cell in oppT:
            cap += 3.5  # prefer flipping enemy territory immediately
        elif cell in unclaimed:
            cap += 1.2  # prefer expanding into unclaimed
        elif cell in selfT:
            cap += 0.2
        else:
            cap += 0.0

        d_t = mindist((nx, ny), targets)
        d_b = mindist((nx, ny), list(opp_boundary)) if opp_boundary else 999999
        val = cap - 0.12 * d_t - 0.18 * d_b

        # small deterministic tie-break: lexicographic by dx,dy order already stable
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]