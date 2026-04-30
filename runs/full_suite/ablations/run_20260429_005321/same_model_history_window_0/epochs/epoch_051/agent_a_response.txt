def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ox, oy = self_pos
    px, py = opp_pos
    obs_set = set((a, b) for a, b in obstacles)
    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev for 8-dir movement
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Fallback: approach center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs_set:
                continue
            v = dist(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best
    parity = observation.get("turn_index", 0) % 2
    best_res = None
    best_score = None
    for rx, ry in resources:
        d_me = dist(ox, oy, rx, ry)
        d_op = dist(px, py, rx, ry)
        if parity == 0:
            score = d_me  # immediate
        else:
            score = (d_me - d_op, d_me)  # reach advantage
        if best_score is None or score < best_score:
            best_score = score
            best_res = (rx, ry)
    rx, ry = best_res
    curr_d = dist(ox, oy, rx, ry)
    # Move greedily towards target, but if already close, break ties by contesting opponent
    best = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs_set:
            continue
        d_new = dist(nx, ny, rx, ry)
        if parity == 0:
            v = (d_new, dist(nx, ny, px, py))
        else:
            d_me = dist(nx, ny, rx, ry)
            d_op = dist(px, py, rx, ry)
            v = (d_me - d_op, d_me, dist(nx, ny, px, py))
        if bestv is None or v < bestv or (d_new == curr_d and v < bestv):
            bestv = v
            best = [dx, dy]
    return best