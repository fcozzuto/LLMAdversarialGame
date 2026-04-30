def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        best = (0, 0, -1e9)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = abs(nx - ox) + abs(ny - oy)
                    val = d
                    if val > best[2]:
                        best = (dx, dy, val)
        return [best[0], best[1]]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_dx, best_dy, best_val = 0, 0, -1e18

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        min_block = 0.0
        min_gain = 0.0
        for rx, ry in resources:
            sd = dist2(nx, ny, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # Encourage resources closer to self; penalize if opponent is closer.
            gain = 1.0 / (sd + 1.0)
            block = (1.0 / (od + 1.0)) - (1.0 / (sd + 1.0))
            # If opponent can reach much sooner, lower attractiveness.
            min_gain += gain
            if od < sd:
                min_block += (sd - od) / (sd + 1.0)

        # Avoid obstacles: penalize being adjacent to obstacles.
        adj = 0
        for ox2, oy2 in obstacles:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                adj += 1

        # Maintain some distance from opponent to reduce contesting.
        oppd = dist2(nx, ny, ox, oy)
        opp_term = oppd / (oppd + 1.0)

        val = (min_gain * 2.0) + (opp_term * 1.5) - (min_block * 1.8) - (adj * 2.5)
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]