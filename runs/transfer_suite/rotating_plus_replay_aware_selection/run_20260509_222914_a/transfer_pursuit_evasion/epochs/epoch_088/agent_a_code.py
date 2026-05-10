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
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Evader targets farthest corner deterministically
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), c[0] * 31 + c[1]))
    tx, ty = target_corner

    best = None
    best_val = None
    d0 = man(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        if is_evader:
            # Prefer increasing distance; also drift toward far corner
            val = (d - d0) * 100 + (man(nx, ny, tx, ty) * 1) - (man(nx, ny, ox, oy) * 0.0)
        else:
            # Pursuer prefers decreasing distance
            val = (d0 - d) * 100 - (man(nx, ny, tx, ty) * 0.05)
        # Tie-break deterministically: lexicographic dx,dy
        key = (val, -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best_val:
            best = [dx, dy]
            best_val = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]