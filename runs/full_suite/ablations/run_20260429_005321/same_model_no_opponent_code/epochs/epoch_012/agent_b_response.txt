def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obst_pen(nx, ny):
        pen = 0
        for px, py in obstacles:
            dd = d2(nx, ny, px, py)
            if dd == 0:
                return 10**9
            if dd <= 1:
                pen += 120
            elif dd <= 4:
                pen += 35
            elif dd <= 9:
                pen += 10
        return pen

    # Primary objective: nearest resource with opponent-aware term; Secondary: avoid obstacles and collisions.
    best_move = (0, 0)
    best_val = -10**18
    if resources:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            min_dr = 10**18
            for rx, ry in resources:
                min_dr = min(min_dr, d2(nx, ny, rx, ry))
            # Encourage progress to a resource while not letting opponent get too close.
            opp_d = d2(nx, ny, ox, oy)
            val = (-min_dr) + (0.15 * opp_d) - obst_pen(nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No visible resources: drift toward center and keep away from opponent/obstacles.
        tx, ty = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            val = (-d2(nx, ny, tx, ty)) + (0.1 * d2(nx, ny, ox, oy)) - obst_pen(nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]