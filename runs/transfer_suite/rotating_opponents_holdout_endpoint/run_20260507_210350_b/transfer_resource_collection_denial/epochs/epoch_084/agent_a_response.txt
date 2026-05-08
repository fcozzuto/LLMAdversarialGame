def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 0, 0)  # (score, dx, dy)

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_res_dist(x, y):
        if not resources:
            return 0
        d0 = 10**9
        for rx, ry in resources:
            d = md(x, y, rx, ry)
            if d < d0:
                d0 = d
        return d0

    # If no known resources, move toward the most likely resource-rich half based on opponent corner.
    if not resources:
        tx = w - 1 if ox <= (w - 1) // 2 else 0
        ty = h - 1 if oy <= (h - 1) // 2 else 0
        resources = [(tx, ty)]

    # Greedy: choose move that minimizes distance to nearest resource; break ties with staying away from opponent slightly.
    cur_target_dist = min_res_dist(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = min_res_dist(nx, ny)
        if nd >= cur_target_dist and (dx != 0 or dy != 0):
            # discourage backtracking unless stuck on top of best distance
            nd = nd + 1
        # slight deterrent from giving opponent an immediate adjacency on resource path
        opp_dist = md(nx, ny, ox, oy)
        score = nd * 100 + (7 - min(7, opp_dist))  # lower is better
        if score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]