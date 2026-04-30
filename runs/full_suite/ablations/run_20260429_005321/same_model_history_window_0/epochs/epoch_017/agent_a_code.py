def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target resource: prefer those we can reach sooner, and where opponent is not advantaged.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        # Advantage: larger when we are closer; penalty if opponent is closer.
        val = (do - ds) * 10 - ds + (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1) * -1
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Evaluate next move deltas.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order_score = 0
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds_next = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        do_next = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        # Encourage moving closer to target, and away from opponent's potential interference.
        dist_opp = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        # Small bias toward staying near resources if no better action.
        near_res = 0
        for rx, ry in resources:
            dres = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if dres == 0:
                near_res = 500
                break
            if dres <= 4:
                near_res = max(near_res, 15 - dres)

        score = (-ds_next * 3) + (dist_opp * 0.2) + (do_next - ds_next) * 0.05 + near_res
        # Deterministic tie-break: prefer earlier in deltas list (and then smaller dx/dy lexicographically).
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
        order_score += 1

    # If all candidate moves blocked/out of bounds, stay.
    dx, dy = best_move
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]