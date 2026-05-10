def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    # Heuristic: pursuer is the one whose role contains "purs", else default to chasing behavior against evader.
    is_pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free_neighbors_count(x, y):
        cnt = 0
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    target_corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1])) if is_pursuer else max(
        corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1])
    )

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps us in place on invalid moves
        d_op = dist2(nx, ny, ox, oy)
        d_corner = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
        free_cnt = free_neighbors_count(nx, ny)

        if is_pursuer:
            # Primary: minimize distance to opponent. Secondary: pull toward the opponent's nearest corner. Tertiary: avoid low-mobility traps.
            score = (-d_op) - 0.08 * d_corner + 0.02 * free_cnt
        else:
            # Evader: maximize distance, keep mobility, and drift toward far corners.
            score = (d_op) - 0.06 * d_corner + 0.03 * free_cnt

        key = (score, -dx, -dy, nx, ny)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]