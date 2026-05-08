def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role", "pursuer")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if role == "evader":
        # Run away from pursuer; also bias toward the farthest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (dist2(nx, ny, ox, oy), dist2(nx, ny, far_corner[0], far_corner[1]), -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[0]), int(best[1])]

    # Pursuer: greedy chase toward opponent with obstacle avoidance; if blocked, choose move that maximizes closeness decrease next step.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # primary: minimize current distance to opponent
        key = (-dist2(nx, ny, ox, oy), -max(dist2(nx, ny, ox + (ox - sx > 0) * 0, oy), 0), -dx, -dy)
        # The second term is just to stabilize ordering; real objective is first term.
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]