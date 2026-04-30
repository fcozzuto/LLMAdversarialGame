def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        dx = 0
        dy = 0
        for nx, ny in ((sx+1, sy),(sx-1, sy),(sx, sy+1),(sx, sy-1),(sx+1,sy+1),(sx+1,sy-1),(sx-1,sy+1),(sx-1,sy-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dx = max(-1, min(1, nx - sx))
                dy = max(-1, min(1, ny - sy))
                break
        return [dx, dy]

    def dist_cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best = None
    best_val = -10**18
    for rx, ry in resources:
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        race = opd - myd
        center = -(abs(rx - cx) + abs(ry - cy))
        # Prefer resources we can race to, then close ones, then central.
        val = race * 30 + (1 if myd <= opd else 0) * 50 - myd * 3 + center * 2
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist_cheb(nx, ny, rx, ry)
        cd = dist_cheb(sx, sy, rx, ry)
        # Move toward target; penalize getting worse; small preference for reducing cheb distance.
        score = (cd - nd) * 20 - nd * 1
        # Secondary: keep away from opponent when tied.
        score += (-dist_cheb(nx, ny, ox, oy)) * 0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]