def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def man(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for r in resources:
            rx, ry = r
            dm = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we're closer or at least not far behind; tie-break deterministically.
            closer_bonus = -1 if dm <= do else 0
            key = (dm + (1 if dm > do else 0) * 2 - (1 if closer_bonus else 0), do, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Evaluate next move by best progress toward (tx,ty), with gentle opponent-disruption via moving away from opponent when not needed.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dm_next = man(nx, ny, tx, ty)
        dm_now = man(sx, sy, tx, ty)
        progress = dm_now - dm_next
        # If progress is equal, move that increases distance to opponent can slow them off-target; otherwise keep neutral.
        opp_dist = man(nx, ny, ox, oy)
        opp_dist_now = man(sx, sy, ox, oy)
        disrupt = opp_dist - opp_dist_now
        # Penalize stepping onto cells adjacent to obstacles a bit (keeps mobility); deterministic.
        near_obs = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in obstacles:
                near_obs += 1
        score = (-dm_next, -(-progress), -opp_dist, disrupt, -near_obs, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]