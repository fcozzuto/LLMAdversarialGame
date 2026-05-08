def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "")
    is_evader = ("evad" in role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    def nearest_obs_d2(x, y):
        best = 999999
        for (px, py) in obstacles:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
        return best if obstacles else 999999

    def edge_penalty(x, y):
        # keep away from hugging edges when evading (more escape routes), less so when pursuing
        d = min(x, w - 1 - x, y, h - 1 - y)
        return -d

    best = None
    best_score = None
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    # Evaluate each legal move from current position.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d2_op = dist2(nx, ny, ox, oy)
        obs_d2 = nearest_obs_d2(nx, ny)
        obs_term = 0 if obs_d2 >= 999999 else obs_d2  # larger is safer/farther from obstacles

        cx_term = -((nx - center_x) ** 2 + (ny - center_y) ** 2)  # closer to center -> higher
        if is_evader:
            score = (d2_op * 1.5) + (obs_term * 0.25) + (cx_term * 0.08)
            score += edge_penalty(nx, ny) * -0.18  # discourage extreme edges
        else:
            # Pursuer: minimize distance, but also try to occupy space that reduces opponent's escape (center bias + obstacle avoidance).
            score = (-d2_op * 1.5) + (obs_term * 0.2) + (cx_term * 0.18)
            score += edge_penalty(nx, ny) * 0.08  # mild preference for middle over edges

        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]