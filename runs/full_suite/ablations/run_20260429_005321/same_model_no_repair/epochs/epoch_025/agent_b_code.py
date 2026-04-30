def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs_set = {tuple(p) for p in obstacles}

    parity = observation.get("turn_index", 0) % 2
    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
    if parity == 1:
        deltas = [[0, 0], [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick a target where we're comparatively closer than the opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources where our ds is smaller than opponent's; tie-break with closeness.
        key = (ds - do, ds, abs(rx - sx) + abs(ry - sy))
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            score = -10**9
        else:
            d_to_t = dist(nx, ny, tx, ty)
            d_from_o = dist(nx, ny, ox, oy)
            # If moving toward target and away from opponent, good; also small penalty for no progress.
            prev_to_t = dist(sx, sy, tx, ty)
            progress = prev_to_t - d_to_t
            score = (progress * 3) + (d_from_o * 0.05) - (d_to_t * 0.001) + (1 if (nx == tx and ny == ty) else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]