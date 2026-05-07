def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king_dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    cur_res_set = set(res)
    if (sx, sy) in cur_res_set:
        return [0, 0]

    def legal(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h):
            return False
        return (nx, ny) not in blocked

    # Heuristic: pick move maximizing guaranteed-first advantage to some resource,
    # with small preference for reducing our closest distance.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        my_best_adv = -10**9
        my_best_close = 10**9
        for rx, ry in res:
            my_d = king_dist(nx, ny, rx, ry)
            op_d = king_dist(ox, oy, rx, ry)
            # Advantage: win if strictly earlier; break ties by favoring shorter my_d.
            adv = (op_d - my_d) * 1000
            if my_d < my_best_close:
                my_best_close = my_d
            if my_d == 0:
                # immediate pickup dominates
                adv += 10**6
            # Encourage paths that move us toward a resource the opponent can't beat
            if adv > my_best_adv:
                my_best_adv = adv

        # Prefer making progress even if no guaranteed win
        score = my_best_adv - my_best_close
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: smaller |dx| then smaller |dy| then lexicographic
            if (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move