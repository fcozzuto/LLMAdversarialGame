def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    is_pursuer = (observation.get("self_role", "pursuer") == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Tie-break: for pursuer prefer advancing toward opponent; for evader prefer moving away.
    best_move = [0, 0]
    best_score = None

    # Precompute escape/pursuit direction signs
    away_x = 0
    if sx != ox:
        away_x = 1 if sx > ox else -1
    away_y = 0
    if sy != oy:
        away_y = 1 if sy > oy else -1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist = d2(nx, ny, ox, oy)

        # Prefer staying near center if distances tie, to avoid corner-locking into obstacles.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if is_pursuer:
            # Minimize distance; small penalty for wandering away from opponent direction.
            # proj>0 means moving toward opponent along axis component.
            proj = 0
            if dx != 0:
                proj += 1 if ((sx + dx) - ox) * (sx - ox) <= 0 else 0
            if dy != 0:
                proj += 1 if ((sy + dy) - oy) * (sy - oy) <= 0 else 0
            score = (-dist, center_pen, -proj)
        else:
            # Maximize distance; tie-break by moving away along both axes when possible.
            proj = 0
            if dx != 0 and dx == away_x:
                proj += 1
            if dy != 0 and dy == away_y:
                proj += 1
            score = (dist, center_pen, proj)

        if best_score is None or score < best_score if is_pursuer else score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]