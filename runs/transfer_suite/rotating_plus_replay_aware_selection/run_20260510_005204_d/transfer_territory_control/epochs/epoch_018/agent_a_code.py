def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Base: move toward opponent if we can flip; otherwise expand into unclaimed.
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_us = abs(nx - sx) + abs(ny - sy)
        center = -(abs(nx - cx) + abs(ny - cy))  # closer to center => higher

        if (nx, ny) in opp_set:
            val = 120 - 3 * d_opp + 2 * center
        elif (nx, ny) in unclaimed:
            val = 80 - 2 * d_opp + 3 * center
        elif (nx, ny) in self_set:
            val = 20 - 2 * d_opp + 1 * center
        else:
            val = 0 - 2 * d_opp + 1 * center

        # If opponent is already closer to the target, penalize to encourage contesting flips.
        # (Deterministic local estimate.)
        opp_d_to_cell = abs(nx - ox) + abs(ny - oy)
        self_d_to_cell = abs(nx - sx) + abs(ny - sy)  # equals 0 or 1 typically
        contest = 0
        if opp_d_to_cell < self_d_to_cell:
            contest -= 10

        # Mild preference to reduce our own distance to opponent while moving.
        val += contest - 1 * d_us

        # Tie-breaker: deterministic ordering by coordinates.
        if val > best_val or (val == best_val and (nx, ny) < (sx + best_dx, sy + best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]