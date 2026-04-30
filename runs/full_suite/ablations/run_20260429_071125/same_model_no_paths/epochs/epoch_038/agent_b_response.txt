def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        opp_d = cheb(nx, ny, ox, oy)

        if resources:
            # Prefer resources where we are closer than the opponent; break ties by smaller my distance.
            score = 10**9
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                adv = op_d - my_d  # higher is better
                cand = (-adv) * 50 + my_d * 5 - opp_d  # minimize
                if cand < score:
                    score = cand
        else:
            # No resources: move toward center while keeping distance from opponent.
            score = cheb(nx, ny, cx, cy) * 5 - opp_d

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: prefer staying still, then smallest dx, then smallest dy.
            if best_move is not None and [dx, dy] != best_move:
                if (dx, dy) == (0, 0):
                    best_move = [dx, dy]
                else:
                    if (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                        best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]