def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    cand = [(dx, dy) for dy in dys for dx in dxs]  # deterministic ordering

    role = (observation.get("self_role") or "").lower()
    self_is_pursuer = "pursuer" in role

    obs_list = list(blocked)

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Wall-aware scoring: prefer staying near obstacles when evading (to emulate wall-run),
    # but prefer away from obstacles when pursuing (to avoid getting trapped).
    def obstacle_proximity(x, y):
        best = 10**9
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best if obs_list else 99

    best = None
    best_score = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_after = dist2(nx, ny, ox, oy)
        prox = obstacle_proximity(nx, ny)

        # corner bias to ensure deterministic long-term direction:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        if self_is_pursuer:
            # pursue: keep moving toward opponent-corner (closest corner to our position)
            corner_target = min(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
            corner_bonus = -dist2(nx, ny, corner_target[0], corner_target[1])
            score = -d_after + 0.20 * corner_bonus
            trap_penalty = 0.35 * prox  # keep away from obstacles while pursuing
            score -= trap_penalty
        else:
            # evade: maximize distance, but also stay close to obstacles to "run walls"
            corner_target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
            corner_bonus = -dist2(nx, ny, corner_target[0], corner_target[1])
            score = d_after + 0.20 * corner_bonus
            wall_bonus = 0.80 * (1.5 / (1 + prox))  # closer obstacles => higher bonus
            score += wall_bonus

        if best is None or (score > best_score + 1e-12) or (abs(score - best_score) <= 1e-12 and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]