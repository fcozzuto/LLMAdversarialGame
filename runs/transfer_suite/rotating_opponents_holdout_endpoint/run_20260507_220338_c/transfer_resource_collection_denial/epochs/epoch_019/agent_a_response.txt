def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    # Focus on a few closest resources (by self distance)
    res_sorted = []
    for rx, ry in resources:
        d = md(sx, sy, rx, ry)
        res_sorted.append((d, rx, ry))
    res_sorted.sort(key=lambda t: t[0])
    top = res_sorted[:6]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Prefer moving onto/near resources and ensure we beat opponent to them.
        for d0, rx, ry in top:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val += 10**9
            else:
                # Higher is better: close to resource and farther than opponent.
                val += (-(sd) + int(od > sd) * 4 + (od - sd) * 0.15)
                # Mild urgency for nearer targets
                val += max(0, (6 - d0)) * 0.2

        # Extra pressure to avoid being surrounded by obstacles (local)
        adj_block = 0
        for ax, ay in moves[:8]:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                adj_block += 1
        val -= adj_block * 0.05

        # Deterministic tie-break: prefer staying closer to the single closest resource
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif abs(val - best_val) < 1e-12:
            # tie: choose minimal md to closest resource, then minimal (dx,dy) lexicographically
            # compute closest-to-any for current and best
            cx1 = sx + dx
            cy1 = sy + dy
            dcur = min(md(cx1, cy1, rx, ry) for _, rx, ry in top)
            bx, by = best
            bx1 = sx + bx
            by1 = sy + by
            dbest = min(md(bx1, by1, rx, ry) for _, rx, ry in top)
            if dcur < dbest:
                best = (dx, dy)
                best_val = val
            elif dcur == dbest and (dx, dy) < best:
                best = (dx, dy)
                best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]