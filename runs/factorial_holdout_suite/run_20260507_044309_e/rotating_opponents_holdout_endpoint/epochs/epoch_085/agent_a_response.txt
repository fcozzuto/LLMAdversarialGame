def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (0, 0)
    best_val = -10**18

    # Opponent archetype: nearest_resource. We try to widen the gap to a resource they are unlikely to beat us to.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate using the best "contested" resource from our next position.
        cur_best = -10**18
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: maximize being closer than opponent; Secondary: prefer shorter paths; Small tie-break to reduce chasing far resources.
            val = (opp_d - self_d) * 1000 - self_d * 3 - (abs(rx - nx) + abs(ry - ny)) * 0.01
            if val > cur_best:
                cur_best = val

        # Additional term: avoid stepping into our own "trap" near obstacles by mild penalty for adjacency count.
        adj_pen = 0
        for ax, ay in candidates[1:]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_pen += 1
        total = cur_best - adj_pen * 2

        if total > best_val:
            best_val = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]