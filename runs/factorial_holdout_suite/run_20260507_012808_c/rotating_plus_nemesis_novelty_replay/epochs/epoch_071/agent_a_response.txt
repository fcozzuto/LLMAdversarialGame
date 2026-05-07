def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            myd = dist(rx, ry, sx, sy)
            opd = dist(rx, ry, ox, oy)
            # If I can win the race, prioritize; if opponent closer, try to deny/retake.
            val = myd - 1.2 * opd
            # Tie-break: prefer nearer resources to reduce switching.
            val = val * 1000 + myd
            if best is None or val < best[0]:
                best = (val, rx, ry)
        _, tx, ty = best
        best_move = None
        for dx, dy, nx, ny in valid_moves:
            # Go towards target; also discourage stepping away from best race outcome.
            base = dist(tx, ty, nx, ny)
            # "Interference": if opponent is closer to some other resource, reduce distance to that first.
            # Lightweight: just consider current target and opponent distance to it after move.
            opp_after = dist(tx, ty, ox, oy)
            myd_after = dist(tx, ty, nx, ny)
            race = myd_after - 1.2 * opp_after
            score = base * 10 + race
            if best_move is None or score < best_move[0]:
                best_move = (score, dx, dy)
        return [int(best_move[1]), int(best_move[2])]

    # No visible resources: move to reduce distance to opponent or move towards center to improve future access.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    aimx, aimy = (cx, cy)
    best_move = None
    for dx, dy, nx, ny in valid_moves:
        score = dist(aimx, aimy, nx, ny) + 0.1 * dist(ox, oy, nx, ny)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)
    return [int(best_move[1]), int(best_move[2])]