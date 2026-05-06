def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best_key = None
    best_move = [0, 0]

    # Precompute resource lists for speed/determinism
    res = [(r[0], r[1]) for r in resources]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        our_min = 10**9
        op_min = 10**9
        # Also track nearest specific resource tie-breakers deterministically
        our_near = None
        op_near = None
        for (rx, ry) in res:
            d1 = manh(nx, ny, rx, ry)
            if d1 < our_min or (d1 == our_min and (rx, ry) < our_near):
                our_min = d1
                our_near = (rx, ry)
            d2 = manh(ox, oy, rx, ry)
            if d2 < op_min or (d2 == op_min and (rx, ry) < op_near):
                op_min = d2
                op_near = (rx, ry)

        # Prefer moves that make it harder for opponent to be closer to resources than we are.
        # Increase "advantage": opponent best distance - our best distance
        adv = op_min - our_min

        # Gentle preference to keep moving toward our nearest and away from opponent when tied
        our_to = our_near if our_near is not None else (0, 0)
        opp_dist = manh(nx, ny, ox, oy)

        # Key: higher adv, then smaller our_min, then closer our_to (lex), then smaller opp_dist
        key = (-adv, our_min, our_to[0], our_to[1], opp_dist, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move