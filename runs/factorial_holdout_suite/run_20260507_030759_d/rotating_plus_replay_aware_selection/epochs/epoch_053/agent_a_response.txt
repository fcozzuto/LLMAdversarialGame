def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    best_target = None
    best_tscore = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        our_d = cd(sx, sy, rx, ry)
        opp_d = cd(ox, oy, rx, ry)
        # Prefer resources we can reach significantly sooner.
        tscore = (opp_d - our_d) * 1000 - our_d
        # Slight tie-break: prefer resources not immediately "behind" obstacles (local proxy).
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = (0, 0)
    best_score = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        our_d2 = cd(nx, ny, tx, ty)
        opp_d2 = cd(ox, oy, tx, ty)
        score = (opp_d2 - our_d2) * 1000 - our_d2
        # Small penalty if we don't get closer (encourage progress but keep determinism).
        if our_d2 >= cd(sx, sy, tx, ty):
            score -= 1
        if score > best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]