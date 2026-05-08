def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cands.append((dx, dy, nx, ny))

    if not cands:
        return [0, 0]

    # local "escape room" heuristic: how many safe neighbors after move
    def escape_room(nx, ny):
        cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                cnt += 1
        return cnt

    # wall proximity penalty (prefer staying away from edges when evading)
    def edge_pen(nx, ny):
        return min(nx, w - 1 - nx) + min(ny, h - 1 - ny)

    best = None
    best_key = None
    if evader:
        # maximize distance to opponent; break ties by maximizing escape room; then prefer more center
        for dx, dy, nx, ny in cands:
            d = man(nx, ny, ox, oy)
            key = (d, escape_room(nx, ny), edge_pen(nx, ny))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
    else:
        # minimize distance to opponent; break ties by maximizing escape room; then prefer more center
        for dx, dy, nx, ny in cands:
            d = man(nx, ny, ox, oy)
            key = (-d, escape_room(nx, ny), edge_pen(nx, ny))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)

    return [int(best[0]), int(best[1])]