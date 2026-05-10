def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_role = observation.get("self_role", "")
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    pursuer = ("purs" in (self_role or "").lower()) or ("catch" in (self_role or "").lower())
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, far_corner[0], far_corner[1])

        # Obstacle pressure: prefer staying away from nearby obstacles
        near_obs = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) <= 1:
                near_obs += 1

        if pursuer:
            # Minimize distance to opponent; also bias toward reducing opponent access to escape corners.
            val = (-d_opp, -d_corner, -near_obs, dx, dy)
        else:
            # Evader: maximize distance from pursuer; also move toward the farthest corner.
            val = (d_opp, d_corner, -near_obs, dx, dy)

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]