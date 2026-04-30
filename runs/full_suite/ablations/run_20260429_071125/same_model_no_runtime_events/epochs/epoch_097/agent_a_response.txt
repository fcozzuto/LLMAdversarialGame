def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Consider only a few closest resources to keep it local/deterministic
    res_sorted = sorted(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
    res_considered = res_sorted[:4] if res_sorted else []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Distance to nearest resource from next position
        if res_considered:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in res_considered)
        else:
            dres = 0

        # Encourage moving away from opponent while still improving resource reach
        dop = cheb(nx, ny, ox, oy)

        # Also slightly prefer moving toward resources that are currently closer to us than to opponent
        closer_bonus = 0
        if res_sorted:
            for rx, ry in res_sorted[:6]:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd <= opd:
                    closer_bonus = 1
                    break

        score = (-dres * 1000) + (dop * 3) + (closer_bonus * 7)

        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]