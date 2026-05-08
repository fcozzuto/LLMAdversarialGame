def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursuer" in str(observation.get("opponent_role", "")).lower())

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def edge_potential(x, y):
        # Prefer central regions when evading (avoid easy corner trap), and prefer edges when pursuing.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy  # 0 at center, larger near edges/corners

    best_score = None
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_ok(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        # Soft "don’t step into immediate obstacle" penalty
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    adj_obs += 1

        # Deterministic tie-break: smaller lexicographic move preferred.
        tie = (dx, dy)

        if pursuer:
            # Pursuer: maximize reduction in distance; avoid clustering near obstacles.
            score = -d2 - 0.3 * adj_obs - 0.02 * edge_potential(nx, ny)
        else:
            # Evader: maximize distance; prefer staying near center to avoid corner walling.
            score = d2 + 0.25 * adj_obs - 0.03 * edge_potential(nx, ny)

        if best_score is None or score > best_score or (score == best_score and tie < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]