def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def min_manhattan_to_set(x, y, S):
        best = 10**9
        for px, py in S:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    opp_points = list(opp_terr) if opp_terr else [(ox, oy)]
    my_points = list(self_terr) if self_terr else [(sx, sy)]

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 7
        if (x, y) in self_terr:
            s += 2
        if (x, y) in opp_terr:
            # flipping on entry, so being able to step into opponent is valuable
            s += 10
        # Prefer expanding the boundary outward from our territory
        adj_my = sum((x + dx, y + dy) in self_terr for dx, dy in dirs4)
        adj_opp = sum((x + dx, y + dy) in opp_terr for dx, dy in dirs4)
        adj_un = sum((x + dx, y + dy) in unclaimed for dx, dy in dirs4)
        s += 3 * adj_my + 2 * adj_un - 4 * adj_opp

        # Steer towards opponent area, but avoid suiciding adjacent to opponent bulk
        d_opp = min_manhattan_to_set(x, y, opp_points)
        s += (9 - min(9, d_opp))  # closer to opp => higher

        # Avoid stepping into immediate opponent neighborhoods too often
        # (deterministic and robust without history)
        if adj_opp >= 3:
            s -= 6

        # Slight preference to keep progressing away from edges already controlled poorly:
        # encourage moving towards the far corner from which opponent started (ox,oy) by attacking line
        d_self_corner = abs((w - 1 - x) - (w - 1 - sx)) + abs((h - 1 - y) - (h - 1 - sy))
        s -= 0.1 * d_self_corner
        return s

    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # deterministic tie-break: prefer lexicographically smaller move deltas after score
        if sc > best or (sc == best and (dx, dy) < (best_move[0], best_move[1])):
            best = sc
            best_move = [dx, dy]
    return best_move