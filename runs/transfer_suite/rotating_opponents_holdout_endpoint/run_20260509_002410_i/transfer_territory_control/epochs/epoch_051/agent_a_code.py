def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set((int(p[0]), int(p[1])) for p in observation.get("self_territory") or [])
    opp_t = set((int(p[0]), int(p[1])) for p in observation.get("opponent_territory") or [])
    unclaimed = set((int(p[0]), int(p[1])) for p in observation.get("unclaimed_cells") or [])

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_list = list(opp_t)
    un_list = list(unclaimed)
    has_opp = bool(opp_list)
    has_un = bool(un_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        gain = 0.0
        if (nx, ny) in opp_t:
            gain += 7.0
        elif (nx, ny) in unclaimed:
            gain += 3.0
        elif (nx, ny) in self_t:
            gain += 0.2
        else:
            gain += 0.6  # likely adjacent unclaimed edge

        dcen = abs(nx - cx) + abs(ny - cy)
        val = gain - 0.15 * dcen

        if has_opp:
            # If we are near opponent territory, prioritize moves that reduce distance to closest opp cell
            close_opp_dist = min(abs(nx - x) + abs(ny - y) for (x, y) in opp_list)
            val += 0.18 * (-close_opp_dist)

        if has_un:
            # Otherwise, drift toward nearest unclaimed
            close_un_dist = min(abs(nx - x) + abs(ny - y) for (x, y) in un_list)
            val += 0.12 * (-close_un_dist)

        # Small tie-break: avoid heading away from opponent position when contests are possible
        val += -0.03 * dist((nx, ny), opp_pos)

        # Another tie-break: prefer staying only if no improving moves
        if (dx, dy) == (0, 0):
            val -= 0.05

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]