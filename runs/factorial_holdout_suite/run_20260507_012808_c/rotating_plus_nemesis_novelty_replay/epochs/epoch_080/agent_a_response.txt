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
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        move_score = -10**18
        for rx, ry in resources:
            myd = md(rx, ry, nx, ny)
            opd = md(rx, ry, ox, oy)

            # Prefer resources I'm not behind on; strongly punish if opponent can get it sooner.
            s = 0
            if myd <= opd:
                s += 1000 - 3 * myd
                # slight preference for preventing opponent from being closer
                s += max(0, 15 - (opd - myd)) * 2
            else:
                s -= 1200 + 5 * (myd - opd) + myd * 0.5

            # Small incentive to approach any promising resource (denial behavior)
            s += max(0, 10 - (opd - myd)) * 1.0

            if s > move_score:
                move_score = s

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]