def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_cells = set(tuple(p) for p in observation.get("self_territory", []))
    opp_cells = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    d_opp_now = abs(x - ox) + abs(y - oy)
    d_center_now = abs(x - cx0) + abs(y - cy0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_s = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            s = -10**14
        else:
            s = 0
            if (nx, ny) in self_cells:
                s += 3
            elif (nx, ny) in opp_cells:
                d_opp_new = abs(nx - ox) + abs(ny - oy)
                s += 10
                s += (d_opp_new - d_opp_now) * 0.35  # counterclaim less if we get closer
            elif (nx, ny) in unclaimed:
                s += 1.5
            else:
                s += 0.5  # other cells are typically low-value unless they help approach

            # Prefer forward pressure away from being stuck: approach opponent when on unclaimed,
            # but retreat slightly if it would enable immediate counterclaim.
            d_opp_new = abs(nx - ox) + abs(ny - oy)
            s += (d_opp_now - d_opp_new) * (0.18 if (nx, ny) in unclaimed else 0.06)

            d_center_new = abs(nx - cx0) + abs(ny - cy0)
            s += (d_center_now - d_center_new) * 0.06  # mild spreading

            # Mild preference to avoid crossing back onto opponent territory after stepping away
            if (nx, ny) in opp_cells:
                s -= 0.15

        if s > best_s:
            best_s = s
            best_move = [dx, dy]

    return best_move