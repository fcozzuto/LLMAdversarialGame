def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    dist0 = cheb(sx, sy, ox, oy)
    can_cap = dist0 == 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if can_cap:
            score = 0
        else:
            # Obstacle pressure: prefer moves that are not "cornered" by nearby obstacles.
            near_obs = 0
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if ex == 0 and ey == 0:
                        continue
                    tx, ty = nx + ex, ny + ey
                    if not (0 <= tx < w and 0 <= ty < h):
                        continue
                    if (tx, ty) in obstacles:
                        near_obs += 1
            if pursuer:
                # Intercept: push toward opponent and slightly bias toward reducing both axes.
                man = abs(nx - ox) + abs(ny - oy)
                score = (-1000 * (d == 0)) + (-10 * d) + (-1 * man) + (-0.5 * near_obs)
            else:
                # Evader: maximize distance, but avoid dead-ends (high obstacle neighborhood).
                man = abs(nx - ox) + abs(ny - oy)
                score = (1000 * (d)) + (2 * man) + (-2 * near_obs)

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            # Deterministic tie-breaker: fixed ordering already, so only update on strict improvement.
            if pursuer:
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]
            else:
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]

    # Fallback (shouldn't happen): stay still
    return best_move