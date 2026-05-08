def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = observation.get("self_territory", []) or []
    op_terr = observation.get("opponent_territory", []) or []
    self_set = set()
    op_set = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))
    for p in op_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            op_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    un_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            un_set.add((int(p[0]), int(p[1])))

    ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    ox, oy = int(ox), int(oy)

    res = observation.get("resources", []) or []
    res_set = set()
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res_set.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Territory-flip and control heuristics
        if (nx, ny) in op_set:
            val = 300
        elif (nx, ny) in un_set:
            val = 200
        elif (nx, ny) in res_set:
            val = 180
        elif (nx, ny) in self_set:
            val = 25
        else:
            val = 5

        # Prefer advancing toward opponent side (counterclaim)
        d_op = abs(nx - ox) + abs(ny - oy)
        val += max(0, 80 - 2 * d_op)

        # Avoid getting boxed near obstacles: penalize if move is surrounded
        adj_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obs:
                adj_obs += 1
        val -= 2 * adj_obs

        # Small tie-breakers deterministic
        val -= 0.1 * (abs(dx) + abs(dy))
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    # If all moves blocked, stay
    return best if best is not None else [0, 0]