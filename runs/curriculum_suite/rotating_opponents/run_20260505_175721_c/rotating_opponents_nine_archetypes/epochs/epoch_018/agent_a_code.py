def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target: prefer resources where we are not farther than opponent; otherwise pick the closest resource.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: we beat/overlap opponent (ds - do smaller). Secondary: shorter ds.
            lead = ds - do
            score = (lead, ds, rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]

    # One-step greedy with obstacle avoidance:
    # If direct diagonal/straight toward target is blocked, try best among neighbors.
    target_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_dy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = []
    if inb(sx + target_dx, sy + target_dy) and not blocked(sx + target_dx, sy + target_dy):
        preferred.append((target_dx, target_dy))
    # Add axis-aligned fallbacks toward target.
    ax1 = (target_dx, 0)
    ax2 = (0, target_dy)
    if inb(sx + ax1[0], sy + ax1[1]) and not blocked(sx + ax1[0], sy + ax1[1]):
        preferred.append(ax1)
    if inb(sx + ax2[0], sy + ax2[1]) and not blocked(sx + ax2[0], sy + ax2[1]):
        preferred.append(ax2)

    # If all preferred blocked/out of bounds, search among neighbors for best move.
    cand_best = None
    for dx, dy in preferred + moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        # Also discourage moving into squares very close to opponent (helps vs safe_collector).
        do_next = cheb(nx, ny, ox, oy)
        # Prefer moves that advance toward target while keeping distance from opponent.
        sc = (ds_next, -do_next, nx, ny)
        if cand_best is None or sc < cand_best[0]:
            cand_best = (sc, (dx, dy))

    if cand_best is None:
        return [0, 0]
    dx, dy = cand_best[1]
    return [int(dx), int(dy)]