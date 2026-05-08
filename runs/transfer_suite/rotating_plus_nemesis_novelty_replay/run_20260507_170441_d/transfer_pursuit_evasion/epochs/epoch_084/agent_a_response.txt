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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not cand:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        # Pick the corner farthest from opponent; then greedily maximize distance to opponent.
        target = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            d_opp = md(nx, ny, ox, oy)
            d_tar = md(nx, ny, target[0], target[1])
            # Tie-break: also maximize distance-to-corner ordering to reduce "orbiting" near target.
            key = (d_opp, d_tar, -nx, -ny, dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]
    else:
        # Pursuer: minimize distance to opponent; tie-break by preferring moves that go toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            d_opp = md(nx, ny, ox, oy)
            d_ctr = abs(nx - cx) + abs(ny - cy)
            # Tie-break: lower center distance to keep mobility and block lines.
            key = (-d_opp, -d_ctr, nx, ny, dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]