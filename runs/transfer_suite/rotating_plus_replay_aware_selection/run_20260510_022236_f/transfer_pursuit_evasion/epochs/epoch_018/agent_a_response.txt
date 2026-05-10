def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("evad" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return (abs(x - cx) + abs(y - cy))  # smaller is better for evader

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        blocked = not ok(nx, ny)
        if blocked:
            nx, ny = sx, sy

        d = dist2(nx, ny, ox, oy)
        neigh = free_neighbors(nx, ny)

        # pursuer: minimize distance; also prefer more free space
        if pursuer:
            score = -d * 100.0 + neigh * 2.0 - (1.0 if blocked else 0.0) * 50.0
        else:
            # evader: maximize distance; avoid tight areas; prefer center
            score = d * 100.0 + neigh * 1.5 - center_bias(nx, ny) * 3.0 - (1.0 if blocked else 0.0) * 50.0

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move