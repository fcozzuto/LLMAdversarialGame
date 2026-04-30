def choose_move(observation):
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort()  # deterministic tie-break

    def in_bounds(x, y):
        return 0 <= x < grid_w and 0 <= y < grid_h

    # Pick a target resource where we have advantage (we're closer than opponent).
    best_t = None
    best_score = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds  # positive means we are closer
        # Encourage nearer targets even if advantage is equal
        score = adv * 100 - ds
        if score > best_score or (score == best_score and (rx, ry) < best_t):
            best_score = score
            best_t = (rx, ry)

    # If no resources, head toward opponent side to increase confrontation likelihood.
    if best_t is None:
        tx, ty = grid_w - 1, grid_h - 1
        if (sx + sy) < (ox + oy):
            tx, ty = 0, 0
        best_t = (tx, ty)

    # Choose move that maximizes utility toward our chosen target, while avoiding obstacles.
    tx, ty = best_t
    best_m = (0, 0)
    best_u = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d1 = dist((nx, ny), (tx, ty))
        d2 = dist((ox, oy), (tx, ty))
        # Move closer; if tied, prefer reducing opponent's advantage (i.e., making us relatively closer).
        u = (-d1 * 10) + (d2 - d1) + (-(abs(tx - nx) + abs(ty - ny)))
        if u > best_u or (u == best_u and (dx, dy) < best_m):
            best_u = u
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]