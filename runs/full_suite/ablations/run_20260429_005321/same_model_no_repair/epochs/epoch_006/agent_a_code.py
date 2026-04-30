def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    def best_target(px, py):
        if not resources:
            return (w // 2, h // 2), -10**9
        best_t = resources[0]
        best_key = None
        for rx, ry in resources:
            sd = md(px, py, rx, ry)
            od = md(ox, oy, rx, ry)
            swing = od - sd  # positive means we are closer / can take sooner
            can_take = 1 if sd <= od else 0
            key = (can_take, swing, -sd, -(rx + 31 * ry))
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        return best_t, best_key[1]

    # One-ply: try moves that stay legal, score by swing of best target from next state
    best_move = (0, 0)
    best_score = None
    target0, _ = best_target(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        t, swing = best_target(nx, ny)
        tx, ty = t
        # Tie-breakers: prefer closer to target, then avoid being far from center
        dist_to_t = md(nx, ny, tx, ty)
        center_dist = abs(nx - w // 2) + abs(ny - h // 2)
        score = (swing, -dist_to_t, -center_dist, -md(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked (shouldn't happen), stay still
    return [best_move[0], best_move[1]]