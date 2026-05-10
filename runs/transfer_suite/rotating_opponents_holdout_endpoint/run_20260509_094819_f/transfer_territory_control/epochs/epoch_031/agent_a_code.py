def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    myc = int(observation.get("self_territory_count", len(selfT)))
    oppc = int(observation.get("opponent_territory_count", len(oppT)))
    aggressive = 1 if myc < oppc else 0  # behind -> flip more aggressively
    opp_entry_weight = 28 + 18 * aggressive
    unclaimed_weight = 60
    self_weight = 5
    center_weight = -2  # closer to center preferred when not immediately expanding

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    unclaimed_list = list(unclaimed)
    have_unclaimed = len(unclaimed_list) > 0

    def nearest_unclaimed_d2(x, y):
        if not have_unclaimed:
            return 10**9
        best = 10**9
        for ux, uy in unclaimed_list:
            d = (ux - x) * (ux - x) + (uy - y) * (uy - y)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            sc = 0
            if (nx, ny) in unclaimed:
                sc += unclaimed_weight
                sc += -0.15 * nearest_unclaimed_d2(nx, ny)
            elif (nx, ny) in oppT:
                sc += opp_entry_weight
            elif (nx, ny) in selfT:
                sc += self_weight
            else:
                sc += 1  # other empty/untracked cells

            sc += center_weight * dist2(nx, ny, cx, cy) ** 0.5

            # Avoid oscillation: prefer not to return to immediate previous unless it improves expansion
            path = observation.get("self_path")  # documented: included each turn = False, but may exist
            if isinstance(path, list) and len(path) >= 2:
                px, py = path[-2]
                if (nx, ny) == (px, py):
                    sc -= 3

        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]