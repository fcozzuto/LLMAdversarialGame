def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def edge_bias(x, y, tx, ty):
        # Prefer moving toward the chosen target side deterministically
        return -(abs((x - tx)) + abs((y - ty)))

    # If no visible resources, drift toward center while keeping away from obstacles
    center = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = 0
        if resources:
            # Choose move that improves advantage to contested resources
            local_best = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Want to be closer than opponent; also break ties deterministically
                s = (do - ds) * 10 - ds
                if (rx, ry) < (0, 0):  # no-op to avoid non-deterministic branches
                    s += 0
                if s > local_best or (s == local_best and (rx, ry) < (best_move[0], best_move[1])):
                    local_best = s
            # Small penalty if getting closer to obstacles is risky (encourage open space)
            adj_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    ax, ay = nx + adx, ny + ady
                    if (ax, ay) in obstacles:
                        adj_obs += 1
            score = local_best - adj_obs
        else:
            # No resources visible: move toward center and away from obstacles
            score = -cheb(nx, ny, center[0], center[1])
            adj_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    if (nx + adx, ny + ady) in obstacles:
                        adj_obs += 1
            score -= 2 * adj_obs
            score += edge_bias(nx, ny, center[0], center[1])

        # Deterministic tie-break: prefer staying, then lexicographically smallest move
        if score > best_score or (score == best_score and ((dx, dy) < best_move)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]