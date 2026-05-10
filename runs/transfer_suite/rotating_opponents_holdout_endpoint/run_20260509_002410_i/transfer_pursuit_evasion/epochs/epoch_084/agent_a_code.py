def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "")
    pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)

        # 1-step lookahead on distance trend
        next_ds = []
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                next_ds.append(cheb(tx, ty, ox, oy))
        if next_ds:
            next_min = min(next_ds)
            next_max = max(next_ds)
        else:
            next_min = d
            next_max = d

        # Score: pursuer wants to minimize distance and its next_min; evader wants to maximize and next_max.
        if pursuer:
            score = (-d) - 0.2 * next_min
        else:
            score = (d) + 0.2 * next_max - 0.03 * cheb(nx, ny, corner[0], corner[1])

        # small deterministic tie-break: prefer staying closer to center for pursuer, farther for evader
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = cheb(nx, ny, cx, cy)
        score += (-0.005 * center_dist) if pursuer else (0.005 * center_dist)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best