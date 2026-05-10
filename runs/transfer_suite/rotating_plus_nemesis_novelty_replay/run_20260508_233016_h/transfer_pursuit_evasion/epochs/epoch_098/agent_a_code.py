def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")
    is_pursuer = ("pursuer" in role) or role.endswith("p")

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0) or 0) % 4
    sep_corner = corners[phase]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx + dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    target_x, target_y = sep_corner
    if is_evader:
        # Evade: prioritize increasing distance, then more mobility, then drift to farthest corner when not aligned with opponent.
        def score(nx, ny):
            d_before = dist(sx, sy, ox, oy)
            d_after = dist(nx, ny, ox, oy)
            corner_push = dist(nx, ny, target_x, target_y)
            return (d_after - d_before) * 100 + mobility(nx, ny) * 2 + corner_push
    else:
        # Pursuer (or unknown): greedy chase with slight corner-separator to limit evader paths.
        def score(nx, ny):
            d_before = dist(sx, sy, ox, oy)
            d_after = dist(nx, ny, ox, oy)
            sep = -dist(nx, ny, target_x, target_y)  # closer to separator corner can help when opponent is heading there
            return (d_before - d_after) * 100 + mobility(nx, ny) * 2 + sep

    best = None
    best_s = None
    # Deterministic tie-break by fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best