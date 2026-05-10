def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_terr = set(tuple(p) for p in observation.get("self_territory", []))
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))
    unclaimed_list = list(unclaimed) if unclaimed else []
    opp_list = list(opp_terr) if opp_terr else []
    opp_center = (observation.get("opponent_position")[0], observation.get("opponent_position")[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Deterministic nearest distance helpers (bounded scans)
    def near_score(cell, targets, bestk=12):
        if not targets:
            return 999
        x, y = cell
        best = 999
        n = 0
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
            n += 1
            if n >= bestk and best == 0:
                break
        return best

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        val = 0.0

        if cell in opp_terr:
            val += 12.0
        elif cell in unclaimed:
            val += 7.0
        elif cell in self_terr:
            val += 1.5

        # Drive toward opponent territory / center; prefer closing distance
        d_opp = abs(opp_center[0] - nx) + abs(opp_center[1] - ny)
        d_before = abs(opp_center[0] - sx) + abs(opp_center[1] - sy)
        val += (d_before - d_opp) * 0.9

        # If we can, prioritize stepping into cells near opponent territory boundary
        boundary_dist = near_score(cell, opp_list, bestk=18)
        val += max(0.0, 6.0 - boundary_dist) * 0.35

        # Or expand toward nearby unclaimed cells
        if unclaimed_list:
            d_neu = near_score(cell, unclaimed_list, bestk=18)
            val += max(0.0, 5.0 - d_neu) * 0.25

        # Mild penalty for staying still to avoid dithering (except when no options)
        if dx == 0 and dy == 0:
            val -= 0.4

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]