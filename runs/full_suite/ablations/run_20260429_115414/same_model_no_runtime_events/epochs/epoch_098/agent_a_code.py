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
    resources = list(set(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if not resources:
            score = cheb(nx, ny, ox, oy)
        else:
            score = -10**9
            for tx, ty in resources:
                d_me = cheb(nx, ny, tx, ty)
                d_op = cheb(ox, oy, tx, ty)
                base = -d_me
                lead = d_op - d_me
                take = 50 if (nx == tx and ny == ty) else 0
                # If opponent is closer, only contest when we can realistically arrive near-competitively
                contest = -5 if lead < 0 and d_me > 2 else 0
                # Prefer stealing/denying key nearby targets
                key = 0
                if d_op <= 2 and d_me <= 3:
                    key = 8
                cand = base + 0.8 * lead + take + key + contest
                if cand > score:
                    score = cand
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]