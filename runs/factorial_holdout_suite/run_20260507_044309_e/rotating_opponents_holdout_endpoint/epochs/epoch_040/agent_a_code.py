def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            resources.append((x, y))
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    order = {m: i for i, m in enumerate(moves)}  # deterministic tiebreak

    best_score = None
    best_move = (0, 0)

    def nearest_score(px, py):
        # returns best (advantage, close_dist) over all resources from (px,py) vs opponent (ox,oy)
        best_adv = None
        best_close = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = dist_manh(px, py, rx, ry)
            d_opp = dist_manh(ox, oy, rx, ry)
            adv = d_opp - d_self
            close = d_self
            if best_adv is None or adv > best_adv or (adv == best_adv and close < best_close):
                best_adv = adv
                best_close = close
        return best_adv, best_close

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        adv, close = nearest_score(nx, ny)
        # Encourage keeping the advantage, and also approaching quickly.
        score = (adv, -close)

        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if score[0] > best_score[0] or (score[0] == best_score[0] and score[1] > best_score[1]):
                best_score = score
                best_move = (dx, dy)
            elif score == best_score:
                if order[(dx, dy)] < order[best_move]:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]