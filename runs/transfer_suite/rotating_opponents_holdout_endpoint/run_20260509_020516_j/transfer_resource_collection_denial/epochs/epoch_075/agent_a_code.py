def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # Candidate moves
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick best target with advantage; prioritize immediate collect race.
    best_target = None
    best_key = None
    for tx, ty in resources:
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        key = (od - sd, -sd, -((tx + ty) & 1))  # maximize opponent distance gap, then closer
        if best_key is None or key > best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target

    # Evaluate each move by resulting advantage over the same target, with small obstacle penalty.
    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        self_after = dist(nx, ny, tx, ty)
        opp_after = dist(ox, oy, tx, ty)  # opponent position fixed this turn
        # Additional tie-break: how well we move toward target row/col parity to match sweep behavior.
        row_align = 0
        if ty == ny:
            row_align = 2
        if tx == nx:
            row_align += 1

        score = (opp_after - self_after, -self_after, row_align, -dist(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]