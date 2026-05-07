def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        moves = [(0, 0)]

    # Choose targets that we can "own" (not necessarily closest), else pick best denial margin.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_dists = []
        for rx, ry in resources:
            sd_next = cd((nx, ny), (rx, ry))
            od_cur = cd((ox, oy), (rx, ry))
            margin = od_cur - sd_next  # positive means we are closer than opponent
            self_dists.append((margin, -sd_next, -rx, -ry, rx, ry))
        self_dists.sort(reverse=True)
        top = self_dists[0]
        margin, neg_sd, _nrx, _nry, rx, ry = top

        # If we have no guaranteed advantage, favor chasing where we can tie/just-beat, and keep away from opponent.
        dist_opp_to_next = cd((ox, oy), (nx, ny))
        val = (margin, neg_sd)
        if margin < 0:
            val = (margin - 0.05 * cd((ox, oy), (rx, ry)), neg_sd - 0.01 * (-dist_opp_to_next))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]