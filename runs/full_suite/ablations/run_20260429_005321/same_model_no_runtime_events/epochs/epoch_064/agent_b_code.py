def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_d_move = cheb(nx, ny, ox, oy)
        if resources:
            best_adv = -10**9
            best_res_dist = 10**9
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                adv = d_opp - d_me  # positive means we are closer now
                # slight preference for nearer resources when tied
                key_d = d_me
                if adv > best_adv or (adv == best_adv and key_d < best_res_dist):
                    best_adv = adv
                    best_res_dist = key_d
            score = 2.0 * best_adv - 0.10 * best_res_dist + 0.05 * opp_d_move
        else:
            # no resources seen: move away from opponent while staying safe
            score = 0.5 * opp_d_move

        # tiny deterministic tie-break: prefer (0,0) less, then lexicographic
        lex = (dx + 1) * 10 + (dy + 1)
        if best is None or score > best or (score == best and lex < (best_move[0] + 1) * 10 + (best_move[1] + 1)):
            best = score
            best_move = [int(dx), int(dy)]

    return best_move