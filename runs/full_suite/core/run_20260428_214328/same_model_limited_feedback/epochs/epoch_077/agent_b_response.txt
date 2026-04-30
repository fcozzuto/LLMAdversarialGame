def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = {(p[0], p[1]) for p in obstacles}
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # If no resources, just stay
    if not resources:
        return [0, 0]

    # Pick a target resource based on who is closer (prefer resources we can reach earlier)
    best = None
    best_key = None
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (md - od, md)  # smaller is better (reach earlier; then closer to us)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose move that gets closer to target while avoiding obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        # primary: reduce distance to target (Chebyshev-ish for diagonal step)
        dist = max(abs(tx - nx), abs(ty - ny))
        # secondary: avoid stepping onto opponent (discourage collisions)
        opp_pen = 0 if (nx, ny) != (ox, oy) else 100
        # small preference for diagonal/advancing to break ties deterministically
        adv = (abs(dx) + abs(dy)) * -0.01
        score = dist + opp_pen + adv
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]