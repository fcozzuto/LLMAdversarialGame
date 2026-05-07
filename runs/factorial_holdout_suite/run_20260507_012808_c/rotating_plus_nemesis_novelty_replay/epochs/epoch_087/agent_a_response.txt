def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        dy = 0
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target that we can reach earlier than the opponent.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Strongly prefer resources where we're closer; break ties toward shorter routes.
        score = (do - ds) * 10 - ds
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best

    # Choose legal move that most reduces distance to target; if tied, keep away from opponent.
    best_moves = []
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = manh(nx, ny, rx, ry)
        d_opp = manh(nx, ny, ox, oy)
        best_moves.append((d_to, -d_opp, dx, dy))
    best_moves.sort()
    if best_moves:
        return [best_moves[0][2], best_moves[0][3]]

    # Fallback: stay or move toward target if possible.
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]