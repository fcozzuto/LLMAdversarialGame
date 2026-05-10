def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def dist_manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_escape_moves_count(x, y, tx, ty):
        # how many safe moves increase distance to (tx,ty)
        c = 0
        d0 = abs(x - tx) + abs(y - ty)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                if abs(nx - tx) + abs(ny - ty) > d0:
                    c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_cur = abs(sx - ox) + abs(sy - oy)
        d_nxt = abs(nx - ox) + abs(ny - oy)
        ed = edge_dist(nx, ny)

        if evader:
            # maximize distance; if tied, avoid states where opponent has many escape-reducing options
            step = (d_nxt - d_cur)
            opp_threat = best_escape_moves_count(nx, ny, ox, oy)  # fewer "worse" moves is better for evader
            score = (step * 10) + (ed * 0.25) + (-opp_threat * 0.05)
            better = (best_score is None) or (score > best_score)
        else:
            # minimize distance; prefer cutting off diagonally and avoid letting opponent gain distance
            step = (d_cur - d_nxt)
            opp_escape = best_escape_moves_count(nx, ny, ox, oy)
            # slight preference for moving toward opponent direction (reduces zigzag effectiveness)
            dir_bonus = (1 if (dx != 0 and dy != 0) else 0) * 0.15
            score = (step * 10) + (ed * -0.05) + (-opp_escape * 0.25) + dir_bonus
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move