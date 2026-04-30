def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    moved = False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        moved = True
        if resources:
            # Denial/attack: prefer targets where opponent is farther than we are.
            # Score favors smaller our distance and larger opponent distance.
            best_rel = -10**18
            best_sd = 10**18
            for tx, ty in resources:
                sd = md(nx, ny, tx, ty)
                od = md(ox, oy, tx, ty)
                rel = od - sd
                if rel > best_rel or (rel == best_rel and sd < best_sd):
                    best_rel = rel
                    best_sd = sd
            # Tie-break also discourages staying still when possible.
            score = best_rel * 1000 - best_sd - (0 if (dx or dy) else 1)
        else:
            # No resources: drift toward center while keeping away from opponent.
            cx, cy = w // 2, h // 2
            score = -md(nx, ny, cx, cy) + 0.001 * md(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if moved else [0, 0]