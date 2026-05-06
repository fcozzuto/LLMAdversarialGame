def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_move = (0, 0)

    # Score each move by the best "winnable" resource it enables, with a safety term vs opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_d_opp = dist((nx, ny), (ox, oy))
        worst_safety = self_d_opp  # prefer staying away

        self_pos = (nx, ny)
        best_resource_tuple = None
        for r in resources:
            sd = dist(self_pos, r)
            od = dist((ox, oy), r)
            # Prioritize resources where we are closer than opponent (od - sd large),
            # then prioritize proximity (smaller sd), then stable tie-break by coordinates.
            tup = (od - sd, -sd, r[0], r[1])
            if best_resource_tuple is None or tup > best_resource_tuple:
                best_resource_tuple = tup

        # If we're equally stuck for all resources, keep away from opponent.
        if best_resource_tuple is None:
            score = (-10**9, worst_safety, 0)
        else:
            score = (best_resource_tuple[0], best_resource_tuple[1], best_resource_tuple[2], best_resource_tuple[3], worst_safety)

        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]