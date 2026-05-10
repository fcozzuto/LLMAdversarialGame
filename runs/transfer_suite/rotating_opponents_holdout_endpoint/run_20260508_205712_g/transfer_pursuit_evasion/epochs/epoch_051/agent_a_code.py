def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "pursuer") or "pursuer").lower()
    pursuer = role != "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Obstacle-aware scoring: prefer moves with better distance objective, then safer/local connectivity, then deterministic tie-break.
    def local_open(x, y):
        cnt = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                cnt += 1
        return cnt

    # Secondary target: if evading, head toward the farthest corner from pursuer; if pursuing, head toward the nearest corner to limit evader escape.
    if pursuer:
        target_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        open_cnt = local_open(nx, ny)
        d_corner = cheb(nx, ny, target_corner[0], target_corner[1])

        # Composite deterministic score. Lower is better when pursuer, higher is better when evader.
        # For pursuer: minimize distance to opponent, avoid dead-ends, and lightly push toward corner target.
        # For evader: maximize distance to opponent, avoid dead-ends, and pull toward corner target.
        if pursuer:
            score = (d_opp, -open_cnt, d_corner)
        else:
            score = (-d_opp, -open_cnt, -d_corner)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]