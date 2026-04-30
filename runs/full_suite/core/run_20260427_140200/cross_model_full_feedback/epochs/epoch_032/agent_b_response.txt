def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    best = [0, 0]
    # If there is a resource, move toward the closest resource while not stepping into obstacle/board.
    if resources:
        best_dist = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # compute distance to nearest resource from candidate
            dist = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            if dist < best_dist:
                best_dist = dist
                best = [dx, dy]
        return best

    # No resources: move to maximize progression toward center while avoiding opponent proximity
    # Prefer moving closer to center (4,4) deterministically, unless blocked or would collide with opponent.
    center = (w // 2, h // 2)
    cx, cy = center
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # distance to center
        dcen = abs(nx - cx) + abs(ny - cy)
        # penalize being too close to opponent (to avoid blocking)
        dist_opp = max(0, max(abs(nx - ox), abs(ny - oy)) - 1)
        score = -dcen - dist_opp * 1
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best