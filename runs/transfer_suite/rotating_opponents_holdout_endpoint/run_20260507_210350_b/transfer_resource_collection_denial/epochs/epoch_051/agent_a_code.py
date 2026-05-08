def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    # Choose target: nearest resource by Manhattan distance
    tx, ty = None, None
    best = 10**9
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d = abs(x - sx) + abs(y - sy)
        if d < best:
            best, tx, ty = d, x, y
    if tx is None:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = -10**18
    # Prefer moves that get closer to target; break ties deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        d_opp_next = abs(tx - (ox + dx)) + abs(ty - (oy + dy))
        gain = (best - d_self)
        # Push to win resources if opponent is closer; otherwise just maximize approach
        contest = (d_opp - d_opp_next)
        score = gain * 10 - max(0, d_self - d_opp) + contest
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move