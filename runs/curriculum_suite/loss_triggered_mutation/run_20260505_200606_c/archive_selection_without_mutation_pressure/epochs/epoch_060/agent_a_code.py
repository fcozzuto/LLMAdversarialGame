def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_tkey = None

    # Choose target that we are more competitive for; otherwise pick one that maximizes "threat" we can steal.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast; otherwise prefer those where we can close the gap.
        # Extra preference for nearer resources to avoid dithering.
        if sd <= od:
            tkey = (0, sd, od - sd, rx, ry)
        else:
            tkey = (1, sd - od, -sd, rx, ry)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    if best_target is None:
        rx, ry = resources[0]
    else:
        rx, ry = best_target

    # Move selection: maximize a step-evaluated objective (distance to chosen target, and reduce opponent access).
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)

        # Simple obstacle-aware repulsion: penalize moves adjacent to obstacles.
        adj_pen = 0
        for ax, ay in ((nx-1, ny-1), (nx, ny-1), (nx+1, ny-1), (nx-1, ny), (nx+1, ny), (nx-1, ny+1), (nx, ny+1), (nx+1, ny+1)):
            if (ax, ay) in obstacles:
                adj_pen += 1

        # Compete for the target: strongly prefer being no farther than opponent (potentially to secure).
        secure_term = 1000 if sd2 <= od2 else 0
        score = secure_term + (od2 - sd2) * 20 - sd2 - adj_pen * 3

        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]