def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    pursuing = ("pur" in self_role) or ("chase" in self_role) or ("pursu" in self_role)
    # In many envs roles are named; fall back: if evading keyword present, treat as evader.
    if "evad" in self_role:
        pursuing = False

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dman(x, y):
        return abs(x - ox) + abs(y - oy)

    def dcheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if inb(nx, ny) and (nx, ny) in obstacles:
                    pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    k = ti % len(moves)
    moves = moves[k:] + moves[:k]

    # Obstacle-aware preference: keep a small "escape route" by favoring squares with more non-obstacle neighbors.
    def mobility(x, y):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    cnt += 1
        return cnt

    best_move = (0, 0)
    best_score = None

    # Deterministic "interception-ish" bias: when pursuing, favor reducing the larger coordinate gap (cuts zigzags).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if pursuing:
            # Primary: minimize Chebyshev (diagonal capture pressure). Secondary: minimize Manhattan.
            # Additional: avoid obstacle-adjacent crowding; prefer higher mobility.
            gapx = abs(nx - ox)
            gapy = abs(ny - oy)
            score = (-dcheb(nx, ny) * 100) - dman(nx, ny) - adj_obs_pen(nx, ny) + mobility(nx, ny)
            # Tie-break: move that reduces the dominant gap.
            if gapx > gapy:
                score += -gapx * 2
            else:
                score += -gapy * 2
        else:
            # Evader: maximize Chebyshev and mobility; avoid obstacle-adjacent squares.
            score = (dcheb(nx, ny) * 100) + dman(nx, ny) + mobility(nx, ny) - adj_obs_pen(nx, ny)

        if best_score is None or (score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]