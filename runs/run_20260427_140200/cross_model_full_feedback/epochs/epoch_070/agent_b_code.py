def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # If no resources visible, move toward the closest resource of the map if any,
        # otherwise stay.
        return [0, 0]

    target = min(resources, key=lambda p: cheb((mx, my), p))

    best_dxdy = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        dist_to_target_now = cheb((mx, my), target)
        dist_to_target_after = cheb((nx, ny), target)

        # Prefer moves that reduce distance to target and keep distance to opponent reasonable
        # Score: negative of next distance to target, minus potential collision with opponent
        score = -dist_to_target_after * 2
        # Bonus if moving closer to opp to contest
        opp_dist_after = cheb((nx, ny), (ox, oy))
        score += max(0, (opp_dist_after - cheb((mx, my), (ox, oy))) * 1)

        if score > best_score:
            best_score = score
            best_dxdy = (dx, dy)

    # Fallback if no legal move found
    if best_dxdy == (0, 0) and not legal(mx, my):
        return [0, 0]

    return [best_dxdy[0], best_dxdy[1]]