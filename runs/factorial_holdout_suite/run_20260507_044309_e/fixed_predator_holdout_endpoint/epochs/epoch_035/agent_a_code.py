def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        # Prefer states where we are closer than opponent; otherwise prefer moves that reduce opp lead.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            if myd == 0:
                score += 2000
            if myd <= oppd:
                # Strongly reward denial and quick pickup
                adv = oppd - myd
                score += 120 - myd + 25 * adv
            else:
                # Opponent closer: try to cut the gap and avoid handing over easy picks
                lead = myd - oppd
                score += -10 * lead - 0.5 * myd

        # Extra: if current move gets us closer to the "best" resource by advantage
        # (helps break ties in a consistent direction)
        score += -0.01 * cheb(nx, ny, sx, sy)

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]