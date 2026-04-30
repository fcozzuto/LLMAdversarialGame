def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, tie, dx, dy)

    # If no resources, move toward center.
    if not resources:
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best_md = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            md = cheb(nx, ny, tx, ty)
            if md < best_md:
                best_md = md
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Evaluate best "lead" on any available resource from this next position.
        best_gain = None  # max over resources of (opp_dist - self_dist) with tie preference
        best_self_d = 0
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gain = opp_d - self_d
            if best_gain is None or gain > best_gain or (gain == best_gain and self_d < best_self_d):
                best_gain = gain
                best_self_d = self_d

        if best_gain is None:
            continue

        # Prefer moves that (a) maximize lead, (b) keep some distance from opponent, (c) avoid diagonals when tied.
        dist_opp = cheb(nx, ny, ox, oy)
        score = best_gain * 1000 + dist_opp
        tie = -(abs(dx) + abs(dy))
        if best is None or score > best[0] or (score == best[0] and tie > best[1]):
            best = (score, tie, dx, dy)

    if best is None:
        return [0, 0]
    return [best[2], best[3]]