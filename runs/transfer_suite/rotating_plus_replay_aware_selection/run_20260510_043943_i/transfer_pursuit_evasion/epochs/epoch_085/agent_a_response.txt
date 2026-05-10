def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_op = cheb(nx, ny, ox, oy)

        # Obstacle proximity penalty (deterministic)
        prox = 0
        for ax, ay in obstacles:
            t = cheb(nx, ny, ax, ay)
            if t == 0:
                prox += 10
            elif t == 1:
                prox += 3
            elif t == 2:
                prox += 1

        if is_evader:
            # Run away from pursuer while drifting to farthest corner from opponent
            drift = -cheb(nx, ny, far_corner[0], far_corner[1])
            val = (d_to_op * 10) + drift - prox * 2
        else:
            # Chase opponent while not blocking near corners (helps corner-crossing less)
            drift = -cheb(nx, ny, near_corner[0], near_corner[1])
            val = (-d_to_op * 10) + drift - prox * 2

        if best_val is None or (val > best_val) if not is_evader else (val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move in cand else [0, 0]