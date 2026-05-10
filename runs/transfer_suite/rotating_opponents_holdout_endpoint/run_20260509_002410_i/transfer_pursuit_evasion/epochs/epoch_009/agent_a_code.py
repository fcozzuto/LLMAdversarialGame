def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("pursuit" in role) or role == "pursuer"

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        d = dist2(nx, ny, ox, oy)
        if pursuer:
            # minimize distance; also prefer center to reduce escape options
            center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            corner_prison = min(dist2(nx, ny, ex, ey) for ex, ey in corners)
            score = (-d) + (-0.12 * center) + (-0.03 * corner_prison)
        else:
            # maximize distance; also bias toward farthest corner from opponent
            far_corner = max(dist2(nx, ny, ex, ey) for ex, ey in corners)
            score = d + (0.08 * far_corner)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move