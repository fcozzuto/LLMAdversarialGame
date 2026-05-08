def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def adj_obst_pen(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role) or ("hunter" in role) or ("chase" in role)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy local move with deterministic tie-break; also biases around "straight-line" obstacle blocks.
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)

        # Prefer moves that keep progressing along the line toward the opponent (or away, if evading).
        prog = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)
        if not pursuer:
            prog = -prog

        # Line-block heuristic: if we're aligned with opponent, avoid stepping into the obstacle corridor.
        line_block = 0
        if sx == ox:
            x = sx
            y0, y1 = sorted([sy, oy])
            for bx, by in obstacles:
                if bx == x and y0 < by < y1:
                    line_block += 1
        if sy == oy:
            y = sy
            x0, x1 = sorted([sx, ox])
            for bx, by in obstacles:
                if by == y and x0 < bx < x1:
                    line_block += 1

        score = d
        if pursuer:
            score += 0.75 * (-prog) + 1.5 * line_block + 0.3 * adj_obst_pen(nx, ny)
        else:
            score = -d + 0.75 * (prog) - 1.5 * line_block + 0.3 * adj_obst_pen(nx, ny)

        if best is None or score < best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]