def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if is_evader:
        far_corner = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), c[0] + 3 * c[1]))
        tx, ty = far_corner
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = man(nx, ny, ox, oy)
            d_goal = man(nx, ny, tx, ty)
            val = (d_opp * 1000) + (d_goal * 3) - (abs(dx) + abs(dy))
            if val > best_val:
                best_val, best = val, (dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[0]), int(best[1])]

    # pursuer
    target = None
    best_val = -10**18
    # prefer moves that reduce distance to opponent; tie-break toward nearest corner to help trapping
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_corner = min(man(nx, ny, cx, cy) for cx, cy in corners)
        # higher is better: want small d_opp and small d_corner => use negatives
        val = (-d_opp * 1000) + (-d_corner * 3) - (abs(dx) + abs(dy) * 0.1)
        if val > best_val:
            best_val, target = val, (dx, dy)
    if target is None:
        return [0, 0]
    return [int(target[0]), int(target[1])]