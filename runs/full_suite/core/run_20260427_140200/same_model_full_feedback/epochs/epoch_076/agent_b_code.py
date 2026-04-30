def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource with a bias against ones opponent is closer to.
    target = None
    best = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # If opponent is very close to the resource, avoid unless we're also close.
        lead = d_op - d_me
        score = -d_me + 0.6 * lead + 0.08 * cheb(rx, ry, w - 1, h - 1)
        # If we're in immediate danger, prefer farther-from-op resources even if slightly worse.
        danger = cheb(sx, sy, ox, oy) <= 2
        if danger:
            score += 0.25 * (cheb(rx, ry, sx, sy) - cheb(rx, ry, ox, oy))
        if score > best:
            best = score
            target = (rx, ry)

    # If no resources, just maximize distance from opponent.
    danger_now = cheb(sx, sy, ox, oy) <= 2
    if target is None:
        target = (sx, sy)

    # Evaluate next moves.
    best_u = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_op_next = cheb(nx, ny, ox, oy)
        d_tar = cheb(nx, ny, target[0], target[1])
        # Base: get closer to target.
        u = -d_tar
        # Safety: strongly avoid reducing distance when near opponent.
        if danger_now:
            u += 3.0 * d_op_next
            # Extra penalty if moving closer.
            u -= 2.0 * max(0, cheb(sx, sy, ox, oy) - d_op_next)
        else:
            u += 0.7 * d_op_next
        # Mild preference for central-ish positions to reduce deadlocks.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        u -= 0.02 * (abs(nx - cx) + abs(ny - cy))
        if u > best_u:
            best_u = u
            best_move = [dx, dy]

    return best_move