def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        if res:
            # Choose a resource where we can beat the opponent's distance advantage.
            val = -10**18
            for rx, ry in res:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources we are closer to than opponent; also prefer smaller self distance.
                v = (do - ds) * 10 - ds
                # Mild tie-break: deterministic preference towards lower x then y.
                v += -0.001 * (rx * 100 + ry)
                if v > val:
                    val = v
            # If opponent is also close to our current best options, be slightly more defensive by not drifting.
            drift_pen = cheb(nx, ny, sx, sy)
            val -= drift_pen
        else:
            # No visible resources: head toward center.
            val = -cheb(nx, ny, center[0], center[1])

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all candidate moves invalid (should be rare), stay still.
    return [int(best_move[0]), int(best_move[1])]