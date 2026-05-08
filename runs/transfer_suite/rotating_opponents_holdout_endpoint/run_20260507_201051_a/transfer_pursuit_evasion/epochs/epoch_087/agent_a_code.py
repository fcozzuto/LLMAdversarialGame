def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("purs", "chaser", "hunter", "seeker", "pursuer"))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def res_score(x, y):
        if not resources:
            return 0
        best = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return -best

    def corner_bonus(x, y):
        corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
        return max(-dist2(x, y, cx, cy) for cx, cy in corners)

    best_move, best_val = (0, 0), None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        val = (-d_opp if is_pursuer else d_opp)
        # deterministic preference: also head toward/away from resources
        val += res_score(nx, ny) * (1 if is_pursuer else -0.5)
        # if evading, slightly prefer far corners
        if not is_pursuer:
            val += corner_bonus(nx, ny) * 0.2
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]