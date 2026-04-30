def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for king moves

    if not resources:
        tx, ty = (W // 2, H // 2)
    else:
        # Pick a resource where we are not worse than the opponent; otherwise pick closest overall.
        best = None
        for r in resources:
            rx, ry = r
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach at least as fast; break ties by smaller ds, then lexicographic.
            key = (0 if ds <= do else 1, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # If immediate target is blocked/unreachable locally, bias toward a nearby alternative resource.
    target = (tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_cur = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)
        # Higher is better
        score = 0
        if (nx, ny) == target:
            score += 1000
        score += 300 - 5 * d_cur
        # Try to keep/extend advantage over opponent at the target
        score += 30 * (d_opp - d_cur)
        # Mild obstacle avoidance: prefer moves that don't step "toward" obstacles too often
        neigh_obs = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                neigh_obs += 1
        score -= 2 * neigh_obs

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]