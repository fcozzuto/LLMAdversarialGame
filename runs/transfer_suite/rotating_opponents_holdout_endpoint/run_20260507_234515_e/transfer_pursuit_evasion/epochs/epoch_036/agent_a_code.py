def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_pursuer = ("purs" in role) or (("direct" in role) and ("evad" not in role)) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def corner_dist(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best_move = [0, 0]
    if self_pursuer:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in oset:
                continue
            d_next = manh(nx, ny, ox, oy)
            if nx == ox and ny == oy:
                score = 10_000_000_000 - (dx == 0 and dy == 0)
            else:
                # Strongly prioritize reducing distance; then prefer cornering (lower corner_dist).
                score = (-d_next) * 10_000 + (-corner_dist(nx, ny))
                # Mild tie-break: stay closer to grid center to avoid corner traps.
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                score += -(abs(nx - cx) + abs(ny - cy))
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # Evader: maximize distance; prefer moving toward farthest corner while keeping safe.
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in oset:
                continue
            d_next = manh(nx, ny, ox, oy)
            if d_next == 0:
                score = -10**18
            else:
                score = d_next * 10_000 + corner_dist(nx, ny) * 10
                # Prefer not to get adjacent too often (soft safety).
                score -= (1 if d_next <= 1 else 0) * 500
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]