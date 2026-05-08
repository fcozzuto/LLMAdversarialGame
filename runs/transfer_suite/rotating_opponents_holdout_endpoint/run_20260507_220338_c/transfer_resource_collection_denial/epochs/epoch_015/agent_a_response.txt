def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    def best_target_score(nx, ny):
        best = -10**30
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                s = 10**9 - i
            else:
                # Prefer resources we can reach earlier (or tie), then closer; penalize far/losing races.
                s = (od - sd) * 1000 - sd - i
            if s > best:
                best = s
        return best

    best_move = [0, 0]
    best_total = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        total = best_target_score(nx, ny)

        # Small anti-greed: if we are not improving race advantage, don't waste a move.
        # Compare current position potential vs moved position potential.
        cur = best_target_score(sx, sy)
        if total < cur:
            total -= 25

        if total > best_total:
            best_total = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]