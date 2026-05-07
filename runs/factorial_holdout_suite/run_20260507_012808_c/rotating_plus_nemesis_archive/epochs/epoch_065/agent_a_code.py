def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        best = (0, 0)
        tx = (w - 1 - ox)
        ty = (h - 1 - oy)
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (ddx, ddy) == (dx, dy):
                return [int(ddx), int(ddy)]
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: minimize (our_dist - opp_dist); i.e., we want to be earlier.
    # Tie-break: smaller our_dist, then deterministic by coordinates.
    best_t = None
    best_val = None
    for (rx, ry) in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        val = sd - od
        key = (val, sd, rx, ry)
        if best_val is None or key < best_val:
            best_val = key
            best_t = (rx, ry)

    rx, ry = best_t
    # Choose a move that reduces our distance to target while staying off obstacles.
    curr_d = manh(sx, sy, rx, ry)
    best_move = (0, 0)
    best_move_key = None
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = manh(nx, ny, rx, ry)
        # Encourage progress; slight preference for moves that also make us earlier vs opp.
        opp_d = manh(ox, oy, rx, ry)
        key = (nd, (nd - opp_d), abs(ddx), abs(ddy), nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (ddx, ddy)

    # If no valid progress move found (rare), just stay.
    if best_move_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]