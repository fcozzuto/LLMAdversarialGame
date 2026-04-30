def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_obs_pen(x, y):
        p = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obstacles:
                    p += 3
        return p

    best_move = None
    best_score = -10**18

    for dx, dy, nx, ny in legal:
        score = -adj_obs_pen(nx, ny)
        score -= 0.1 * md(nx, ny, ox, oy)
        if resources:
            best_res = None
            best_res_val = -10**18
            for rx, ry in resources:
                my_d = md(nx, ny, rx, ry)
                opp_d = md(ox, oy, rx, ry)
                margin = opp_d - my_d  # positive => I am closer after this move
                val = 1000 * margin - my_d
                if val > best_res_val:
                    best_res_val = val
                    best_res = (rx, ry)
            score += best_res_val
        if best_move is None or score > best_score or (score == best_score and (dx, dy) < best_move[:2]):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]