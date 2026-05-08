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

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evad" in role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_prev = dist2(sx, sy, ox, oy)
        d_new = dist2(nx, ny, ox, oy)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        corner_bias = -dist2(nx, ny, tx, ty) + edge * 0.05

        if nx == ox and ny == oy:
            score = -10**15 if is_evader else 10**15
        else:
            if is_evader:
                score = d_new * 5.0 + corner_bias - max(0, d_new - d_prev) * 0.2
            else:
                score = (d_prev - d_new) * 5.0 + corner_bias - 0.02 * d_new

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]