def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
    resources = observation.get("resources", []) or []
    resources = [(int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2 and 0 <= int(r[0]) < w and 0 <= int(r[1]) < h and (int(r[0]), int(r[1])) not in blocked]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not inside(int(sx), int(sy)):
        for dx, dy in moves:
            nx, ny = int(sx) + dx, int(sy) + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not resources:
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Move away from opponent to reduce stealing
            val = (abs(nx - ox) + abs(ny - oy))
            if val > (abs(best[0] - ox) + abs(best[1] - oy)):
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**9
    best_tiebreak = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # After moving, consider best resource to contest (maximize opponent advantage gap)
        score = -10**9
        nearest_self = 10**9
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            # Prefer resources we can reach sooner; also bias toward those where we are already ahead
            g = (do - ds)
            if g > score:
                score = g
            if ds < nearest_self:
                nearest_self = ds
        # If tied, take closer resource; if still tied, prefer larger "advantage"
        if score > best_score or (score == best_score and nearest_self < best_tiebreak):
            best_score = score
            best_tiebreak = nearest_self
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]