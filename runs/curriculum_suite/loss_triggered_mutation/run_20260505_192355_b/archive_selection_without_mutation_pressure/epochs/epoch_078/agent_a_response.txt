def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_same_row = 1 if oy == sy else 0
    opp_row_close = 1 if abs(oy - sy) <= 1 else 0

    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Predictive: choose a target by how much better we are than opponent from our next position
        local_best_gap = -10**18
        local_self_d = 10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            gap = od - sd
            if gap > local_best_gap or (gap == local_best_gap and sd < local_self_d):
                local_best_gap = gap
                local_self_d = sd

        # Anti-sweep: if opponent is aligned with our row, prefer moves that change our row to avoid being "swept"
        row_penalty = 0
        if opp_same_row:
            row_penalty = 2 if ny == sy else 0
        elif opp_row_close:
            row_penalty = 1 if ny == sy else 0

        # Prefer staying on/near resources as a secondary objective
        opp_d_now = dist(ox, oy, nx, ny)
        val = 1000 * local_best_gap - local_self_d - row_penalty + (opp_d_now // 2)

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]