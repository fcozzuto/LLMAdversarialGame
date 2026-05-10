def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Assume: if opponent is pursuer, it greedily moves to minimize distance.
    sr = str(observation.get("self_role") or "").lower()
    am_evader = not (("pursuer" in sr) or ("pred" in sr) or ("catch" in sr) or ("hunter" in sr))

    def opp_greedy(px, py):
        bestd = None
        best = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = dist(nx, ny, sx, sy)
            if bestd is None or d < bestd:
                bestd = d
                best = [(nx, ny)]
            elif d == bestd:
                best.append((nx, ny))
        if not best:
            return px, py
        # Deterministic tie-break: prefer larger distance in x, then y from my position
        best.sort(key=lambda p: (abs(p[0] - sx), abs(p[1] - sy), p[0], p[1]), reverse=True)
        return best[0]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Score from my perspective:
        # primary: maximize distance after my move and opponent greedy response
        if am_evader:
            ex, ey = opp_greedy(ox, oy)
            score = dist(nx, ny, ex, ey) * 3
            # secondary: avoid being adjacent to opponent after its response
            score -= (1 if dist(nx, ny, ex, ey) <= 1 else 0) * 5
            # tertiary: prefer staying away from obstacles by maximizing open neighbors
            open_n = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay):
                    open_n += 1
            score += open_n * 0.2
        else:
            # If I'm pursuer, greedy pursuit with obstacle avoidance
            score = -dist(nx, ny, ox, oy) * 3
            ex, ey = opp_greedy(ox, oy)
            score += -dist(nx, ny, ex, ey) * 0.5

        # Deterministic tie-break: prefer moves with larger dx, then larger dy, then smallest magnitude
        key = (score, dx, dy, -abs(dx) - abs(dy))
        if best_score is None or key > (best_score, best_move[0], best_move[1], -abs(best_move[0]) - abs(best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]