def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obs_list)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        me0 = abs(nx - ox) + abs(ny - oy)
        best_res = None
        best_res_val = None

        for tx, ty in resources:
            d_me = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me  # positive means we are closer now
            v = lead * 2000 - d_me * 3 + (1 if tx == nx or ty == ny else 0) - 0.001 * me0
            if best_res_val is None or v > best_res_val or (v == best_res_val and (d_me, d_opp, tx, ty) < best_res):
                best_res_val = v
                best_res = (d_me, d_opp, tx, ty)

        if best_val is None or best_res_val > best_val or (best_res_val == best_val and (nx, ny) < (best_move[0], best_move[1])):
            best_val = best_res_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]