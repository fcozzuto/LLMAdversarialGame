def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        cell = (nx, ny)
        if cell in obstacles:
            continue

        base = 0
        if cell in opp_t:
            base += 6  # likely flips on entry
        elif cell in unclaimed:
            base += 3  # claim new territory
        elif cell in self_t:
            base += 1  # safe expansion/continuation

        # Prefer central control and moving away from opponent to reduce counterclaim
        cen = -dist2(nx, ny, cx, cy) * 0.001
        away = dist2(nx, ny, ox, oy) * 0.002

        # If we can directly threaten opponent boundary, slightly favor that
        # by moving toward any opponent-occupied cell when not stepping into it.
        toward_opp_boundary = 0
        if cell not in opp_t and opp_t:
            toward_opp_boundary = -min(dist2(nx, ny, ex, ey) for (ex, ey) in opp_t) * 0.0005

        # Deterministic tie-breaker: lexicographic on (dx,dy)
        key = (-(base + cen + away + toward_opp_boundary), abs(dx) + abs(dy), nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]