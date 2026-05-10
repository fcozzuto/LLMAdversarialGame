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
    d_self_center_now = abs(x - cx0) + abs(y - cy0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def dist_to_center(nx, ny):
        return abs(nx - cx0) + abs(ny - cy0)

    best_s = -10**18
    best = [0, 0]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            s = -10**15  # invalid move; engine would keep us, but avoid wasting
        else:
            s = 0
            if (nx, ny) in self_cells:
                s += 2
            elif (nx, ny) in opp_cells:
                s += 9
                # If entering opp area, prefer to also increase our distance from opponent (reduce counter-capture)
                d_opp = abs(nx - ox) + abs(ny - oy)
                s += 3 if d_opp >= d_opp_now else -1
            elif (nx, ny) in unclaimed:
                s += 7
                # Prefer expanding toward center and away from opponent to out-territory
                s += 4 if dist_to_center(nx, ny) < d_self_center_now else -1
                d_opp = abs(nx - ox) + abs(ny - oy)
                s += 3 if d_opp > d_opp_now else 0
            else:
                # unlisted neutral: still allow progress toward center
                s += 1
                s += 2 if dist_to_center(nx, ny) < d_self_center_now else -1

            # Tie-breakers: prefer smaller distance to center, then prefer farther from opponent (safer spread)
            s -= dist_to_center(nx, ny) * 0.1
            s -= (abs(nx - ox) + abs(ny - oy)) * 0.01

        if s > best_s:
            best_s = s
            best = [dx, dy]

    return best