def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    c += 1
        return c

    def goal_priority(nx, ny):
        if not resources:
            return -10**9
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If opponent is already much closer, only pursue if we can reduce the gap.
            gap_before = cheb(sx, sy, rx, ry) - d_opp
            gap_after = d_self - d_opp
            contest = 1.0 if gap_after <= 0 else 0.0
            score = (gap_before - gap_after) * 6.0 + contest * 20.0
            # Encourage moving to nearer resources in general.
            score -= d_self * 1.5
            # Avoid getting boxed in.
            score -= adj_obst(nx, ny) * 2.5
            # Small bias to not drift aimlessly.
            score -= cheb(sx, sy, nx, ny) * 0.1
            if score > best:
                best = score
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        v = goal_priority(nx, ny)
        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically after value
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]