def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set(obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: resource that makes us relatively closer than opponent (minimize self_dist - opp_dist).
    best_r = None
    best_key = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        key = (self_d - opp_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = None
    best_cand = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_to_target = man(nx, ny, tx, ty)
        # Secondary: move that also reduces opponent-to-target distance.
        opp_to_target = man(ox, oy, tx, ty)
        cand = (d_to_target, -opp_to_target, dx, dy, nx, ny)
        if best_cand is None or cand < best_cand:
            best_cand = cand
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move