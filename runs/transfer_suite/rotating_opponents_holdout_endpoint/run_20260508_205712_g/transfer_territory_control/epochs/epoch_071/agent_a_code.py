def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    turn = int(observation.get("turn_index", 0) or 0)

    # Directional pressure: move away from opponent early; else move toward center then into unclaimed.
    awayx = 1 if sx <= cx else -1
    awayy = 1 if sy <= cy else -1
    early = turn < 10

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            cell_score = 120 - (abs(nx - ox) + abs(ny - oy))  # prioritize counter-flip
        elif (nx, ny) in un_set:
            cell_score = 70 - (abs(nx - cx) + abs(ny - cy))  # secure frontier/claim
        elif (nx, ny) in self_set:
            cell_score = 10 - (abs(nx - cx) + abs(ny - cy))  # consolidate
        else:
            cell_score = 0

        # Encourage progress: reduce distance to the chosen direction; avoid oscillation poorly
        if early:
            prog = -abs((nx - sx) * awayx) - abs((ny - sy) * awayy)
        else:
            prog = -(abs(nx - cx) + abs(ny - cy)) * 0.2

        # Prefer moving (tie-break): don't stay if equally good
        move_pen = 0 if (dx == 0 and dy == 0) else -1

        score = cell_score + prog + move_pen
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move