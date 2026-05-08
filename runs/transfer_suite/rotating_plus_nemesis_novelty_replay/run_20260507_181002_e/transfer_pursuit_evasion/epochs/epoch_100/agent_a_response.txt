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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        dc = (nx - far_corner[0]) * (nx - far_corner[0]) + (ny - far_corner[1]) * (ny - far_corner[1])

        if is_evader:
            # Primary: increase distance. Secondary: head to farthest corner.
            score = (d, -dc)
            better = (best is None) or (score[0] > best_score[0]) or (score[0] == best_score[0] and score[1] > best_score[1])
        else:
            # Primary: decrease distance to opponent. Secondary: still prefer moving toward opponent's local direction.
            # Using squared distance for smoother tie-break.
            sd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = (-d, -sd)
            better = (best is None) or (score[0] > best_score[0]) or (score[0] == best_score[0] and score[1] > best_score[1])

        if better:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best