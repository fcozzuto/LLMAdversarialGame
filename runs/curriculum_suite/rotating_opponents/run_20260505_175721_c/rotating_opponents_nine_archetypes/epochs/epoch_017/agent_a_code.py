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

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        candidates = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = ds - do  # smaller => we are at least as close
            candidates.append((lead, ds, rx, ry))
        candidates.sort()
        # Prefer a target where we are not behind; if all behind, take the least behind.
        best_lead = candidates[0][0]
        top = [c for c in candidates if c[0] == best_lead]
        c = top[0]  # deterministic
        _, _, tx, ty = c

    best_move = (0, 0)
    best_score = -10**9
    cur_ds = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Main: reduce distance to target; Secondary: keep away from opponent probe; Tertiary: improve relative capture chance.
        rel_now = cur_ds - cheb(ox, oy, tx, ty)
        rel_next = ns - cheb(ox, oy, tx, ty)
        score = (cur_ds - ns) * 10 - no * 0.5 + (rel_now - rel_next) * 4
        # If resources exist, add a small incentive to be closer than opponent to the chosen target.
        if resources:
            score += (cheb(ox, oy, tx, ty) - ns) * 2
        # Deterministic tie-break: prefer moves with smaller dx, then dy (via tuple compare)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]