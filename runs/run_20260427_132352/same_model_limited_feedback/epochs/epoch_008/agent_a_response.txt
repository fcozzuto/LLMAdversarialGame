def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Pick resource with best "advantage": (opp_dist - self_dist) maximized
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        t = (rx, ry)
        adv = dist(opp_pos, t) - dist(self_pos, t)
        if adv > best_adv:
            best_adv = adv
            best_t = t
        elif adv == best_adv and t < best_t:
            best_t = t
    tx, ty = best_t

    # Prefer blocking/contesting if opponent is very close
    if dist(self_pos, opp_pos) <= 1:
        # Re-select target to the resource where we are relatively closest (more likely to deny)
        best_t2 = None
        best_gap = 10**9
        for rx, ry in resources:
            selfd = dist(self_pos, (rx, ry))
            oppd = dist(opp_pos, (rx, ry))
            gap = (selfd - oppd)  # smaller means we are closer or equally close
            if gap < best_gap or (gap == best_gap and (rx, ry) < best_t2):
                best_gap = gap
                best_t2 = (rx, ry)
        tx, ty = best_t2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        new_selfd = dist((nx, ny), (tx, ty))
        oppd = dist(opp_pos, (tx, ty))
        score = (oppd - new_selfd) * 1000 - new_selfd
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If everything was blocked (should be rare), fall back to any legal move
    if best_score == -10**18:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]