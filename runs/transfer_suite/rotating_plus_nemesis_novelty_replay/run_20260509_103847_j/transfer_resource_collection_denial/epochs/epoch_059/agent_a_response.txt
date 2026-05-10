def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick a target deterministically: prefer resources where we are closer than opponent; else denier where opp advantage is largest.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Phase: secure (ds<=do) prioritized by larger margin; otherwise contest by smaller ds and large do advantage.
        if ds <= do:
            key = (0, -(do - ds), ds, rx, ry)
        else:
            key = (1, (do - ds), ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    # Choose move that reduces our distance to target; if tie, increase opponent distance; avoid obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        # Also penalize staying unless forced.
        move_pen = 1 if (dx == 0 and dy == 0) else 0
        # Prefer getting closer; then keep farther from opponent to avoid being blocked.
        key = (self_d, move_pen, -opp_d, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is not None:
        return best_move[1]

    # If surrounded by obstacles, deterministically try any in-bounds non-blocked move; else stay.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]