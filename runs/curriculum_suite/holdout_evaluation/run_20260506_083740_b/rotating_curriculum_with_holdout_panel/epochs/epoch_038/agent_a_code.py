def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in ob
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2

    best_move = (0, 0)
    best_score = None

    # New strategic change: evaluate moves by the maximum contested advantage over all resources
    # (how much closer we are than the opponent), not just a single preselected target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = None
        my_to_center = md(nx, ny, cx, cy)

        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in ob:
                continue
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            # Primary: contested advantage (positive if we are closer than opponent)
            # Secondary: avoid chasing far-off resources; small pressure to move toward center.
            # Extra: slightly penalize if we would be slower than opponent by a lot.
            advantage = (oppd - myd)
            s = advantage * 12 - md(rx, ry, cx, cy) - max(0, myd - oppd) * 2
            if move_score is None or s > move_score:
                move_score = s

        if move_score is None:
            continue

        # Tie-break deterministically: prefer higher score, then smaller center distance, then lexicographic move.
        tie = (-my_to_center, dx, dy)
        total = (move_score, tie)
        if best_score is None or total[0] > best_score[0] or (total[0] == best_score[0] and tie < best_score[1]):
            best_score = (total[0], total[1])
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]