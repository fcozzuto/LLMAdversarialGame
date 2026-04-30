def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    if not resources:
        # Move toward center deterministically
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (-dist2(nx, ny, tx, ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]

    opp_pos = (ox, oy)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        for rx, ry in resources:
            selfd = dist2(nx, ny, rx, ry)
            oppd = dist2(opp_pos[0], opp_pos[1], rx, ry)
            if selfd == 0:
                score += 10**9
            else:
                score += (oppd - selfd)
        # Small tie-break: prefer closer to opponent to contest, but not at expense of resources due to big bonus.
        score += -dist2(nx, ny, opp_pos[0], opp_pos[1]) // 10

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]