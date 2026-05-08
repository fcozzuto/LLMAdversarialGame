def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d = abs(ax - bx) + abs(ay - by)
        return d

    # immediate capture if we can move onto opponent
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny) and nx == ox and ny == oy:
            return [dx, dy]

    # 1-step minimax: we move, opponent then moves to maximize distance; we minimize that.
    best_move = [0, 0]
    best_score = None

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_farness(x, y):
        # prefer breaking toward the most distant corner from us (opponent tendency)
        return max(man(x, y, cx, cy) for cx, cy in corners)

    for dx, dy in dirs:
        nsx, nsy = sx + dx, sy + dy
        if not ok(nsx, nsy):
            continue
        # opponent chooses move
        opp_best = -1
        opp_best_f = -1
        for odx, ody in dirs:
            nosx, nosy = ox + odx, oy + ody
            if not ok(nosx, nosy):
                continue
            # if opponent can capture by moving onto us, they would prefer it
            if nosx == nsx and nosy == nsy:
                opp_best = 10**9
                opp_best_f = 10**9
                break
            d = man(nosx, nosy, nsx, nsy)
            f = corner_farness(nosx, nosy)
            if d > opp_best or (d == opp_best and f > opp_best_f):
                opp_best = d
                opp_best_f = f

        # evaluate: minimize opponent's best distance; tie-break chase toward closest-to-us corner control
        if best_score is None or opp_best < best_score:
            best_score = opp_best
            best_move = [dx, dy]
        elif opp_best == best_score:
            # tie-break: choose our move that reduces our distance to opponent most
            if man(nsx, nsy, ox, oy) < man(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = [dx, dy]
            else:
                # final deterministic tie-break
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]