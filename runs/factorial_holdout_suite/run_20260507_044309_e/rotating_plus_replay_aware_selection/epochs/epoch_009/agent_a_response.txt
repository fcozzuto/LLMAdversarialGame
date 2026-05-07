def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2

    def opp_next_toward(rx, ry):
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        px, py = ox + step_x, oy + step_y
        if blocked(px, py):
            return None
        return (px, py)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Evaluate by best "claim" resource from this next position
        val = -1e18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Bonus if opponent's greedy approach to this resource is blocked next step
            opp_pos = opp_next_toward(rx, ry)
            opp_block_bonus = 3.0 if opp_pos is None else 0.0

            # Tie-break: prefer earlier arrival and, if close, more central/less commitment
            score = (d_opp - d_me) * 10.0 - d_me * 1.0 + (1.5 if (rx, ry) == (ox, oy) else 0.0) + opp_block_bonus
            score += (-(cheb(nx, ny, cx, cy)) * 0.05)
            if score > val:
                val = score

        # Deterministic tie-break order by (best_val, dx, dy)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]