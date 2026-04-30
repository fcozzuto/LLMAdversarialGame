def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        if (tx, ty) in obs:
            tx, ty = sx, sy
        resources = [(tx, ty)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target resource where we have the biggest distance advantage over the opponent.
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        d_s = man(sx, sy, rx, ry)
        d_o = man(ox, oy, rx, ry)
        adv = d_o - d_s
        # Small tie-break to prefer nearer targets to avoid dithering
        score = adv * 1000 - d_s
        if score > best_adv:
            best_adv = score
            best_target = (rx, ry)

    tr, tt = best_target

    # Choose the next move that most reduces distance to target; tie-break by moving away from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_now = man(sx, sy, tr, tt)
        d_next = man(nx, ny, tr, tt)
        progress = d_now - d_next
        sep_now = man(sx, sy, ox, oy)
        sep_next = man(nx, ny, ox, oy)
        sep_gain = sep_next - sep_now
        # Also lightly prefer staying aligned with target direction by avoiding sideways moves when possible.
        align = -(abs((nx - sx) - (tr - sx) // (abs(tr - sx) + 1)) + abs((ny - sy) - (tt - sy) // (abs(tt - sy) + 1)))
        val = progress * 1000 + sep_gain * 10 + align
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]